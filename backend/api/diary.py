"""Shared date diary API."""

import os
from datetime import date, datetime, timedelta
from calendar import monthrange

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from models import DailyPhoto, DailyNote, Order, SpecialDate
from extensions import db
from config import Config
from api import diary_bp


def get_month_range(year, month):
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


@diary_bp.route('/diary', methods=['GET'])
@jwt_required()
def get_month_diary():
    """Get monthly calendar overview."""
    now = datetime.utcnow()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    start, end = get_month_range(year, month)

    # Orders in this month
    orders = Order.query.filter(
        Order.created_at >= start,
        Order.created_at < end + timedelta(days=1)
    ).all()
    order_dates = {}
    for o in orders:
        d = o.created_at.date().isoformat() if hasattr(o.created_at, 'date') else str(o.created_at)[:10]
        order_dates[d] = order_dates.get(d, 0) + 1

    # Photos in this month
    photos = DailyPhoto.query.filter(
        DailyPhoto.date >= start, DailyPhoto.date <= end
    ).all()
    photo_dates = {}
    for p in photos:
        ds = p.date.isoformat() if hasattr(p.date, 'isoformat') else str(p.date)
        photo_dates[ds] = photo_dates.get(ds, 0) + 1

    # Notes in this month
    notes = DailyNote.query.filter(
        DailyNote.date >= start, DailyNote.date <= end
    ).all()
    note_dates = {}
    for n in notes:
        ds = n.date.isoformat() if hasattr(n.date, 'isoformat') else str(n.date)
        note_dates[ds] = note_dates.get(ds, 0) + 1

    # Moods in this month (per-user, per-date)
    mood_dates = {}
    for n in notes:
        if n.mood:  # only include notes that have a mood
            ds = n.date.isoformat() if hasattr(n.date, 'isoformat') else str(n.date)
            if ds not in mood_dates:
                mood_dates[ds] = []
            mood_dates[ds].append({
                'user_id': n.user_id,
                'nickname': n.user.nickname if n.user else '',
                'mood': n.mood,
            })

    # Special dates in this month
    specials = SpecialDate.query.filter(
        db.func.strftime('%m', SpecialDate.date) == f'{month:02d}'
    ).all()

    return jsonify({
        'year': year, 'month': month,
        'order_dates': order_dates,
        'photo_dates': photo_dates,
        'note_dates': note_dates,
        'mood_dates': mood_dates,
        'special_dates': [s.to_dict() for s in specials],
    }), 200


@diary_bp.route('/diary/<string:diary_date>', methods=['GET'])
@jwt_required()
def get_date_detail(diary_date):
    """Get detail for a specific date."""
    try:
        d = date.fromisoformat(diary_date)
    except ValueError:
        return jsonify({'msg': '日期格式错误，需为YYYY-MM-DD'}), 400

    photos = DailyPhoto.query.filter_by(date=d).order_by(DailyPhoto.created_at.desc()).all()
    notes = DailyNote.query.filter_by(date=d).order_by(DailyNote.created_at.desc()).all()

    # Orders on this date
    next_day = d + timedelta(days=1)
    orders = Order.query.filter(
        Order.created_at >= d,
        Order.created_at < next_day
    ).order_by(Order.created_at.desc()).all()

    return jsonify({
        'date': diary_date,
        'photos': [p.to_dict() for p in photos],
        'notes': [n.to_dict() for n in notes],
        'orders': [o.to_dict(include_items=False) for o in orders],
    }), 200


@diary_bp.route('/diary/<string:diary_date>/photos', methods=['POST'])
@jwt_required()
def upload_diary_photo(diary_date):
    """Upload photo to diary."""
    current_user = get_current_user()
    try:
        d = date.fromisoformat(diary_date)
    except ValueError:
        return jsonify({'msg': '日期格式错误'}), 400

    if 'file' not in request.files:
        return jsonify({'msg': '请选择文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'msg': '请选择文件'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'msg': f'不支持的图片格式'}), 400

    # Save to diary/YYYY/MM/
    import uuid
    folder = os.path.join(Config.UPLOAD_DIARY, str(d.year), f'{d.month:02d}')
    os.makedirs(folder, exist_ok=True)
    filename = f'{diary_date}_{uuid.uuid4().hex[:8]}.{ext}'
    file.save(os.path.join(folder, filename))

    photo = DailyPhoto(
        user_id=current_user.id,
        date=d,
        image_path=f'diary/{d.year}/{d.month:02d}/{filename}',
    )
    db.session.add(photo)
    db.session.commit()

    return jsonify({'photo': photo.to_dict()}), 201


@diary_bp.route('/diary/photos/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_diary_photo(photo_id):
    current_user = get_current_user()
    photo = DailyPhoto.query.get_or_404(photo_id)

    if photo.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'msg': '无权删除'}), 403

    # Delete file
    filepath = os.path.join(Config.UPLOAD_FOLDER, photo.image_path)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()
    return jsonify({'msg': '照片已删除'}), 200


@diary_bp.route('/diary/<string:diary_date>/notes', methods=['POST'])
@jwt_required()
def create_diary_note(diary_date):
    current_user = get_current_user()
    try:
        d = date.fromisoformat(diary_date)
    except ValueError:
        return jsonify({'msg': '日期格式错误'}), 400

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'msg': '日记内容不能为空'}), 400

    note = DailyNote(
        user_id=current_user.id,
        date=d,
        content=content,
        mood=data.get('mood', ''),
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({'note': note.to_dict()}), 201


@diary_bp.route('/diary/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_diary_note(note_id):
    current_user = get_current_user()
    note = DailyNote.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        return jsonify({'msg': '只能编辑自己的日记'}), 403

    data = request.get_json()
    if 'content' in data:
        note.content = data['content'].strip()
    if 'mood' in data:
        note.mood = data['mood']
    db.session.commit()

    return jsonify({'note': note.to_dict()}), 200


@diary_bp.route('/diary/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_diary_note(note_id):
    current_user = get_current_user()
    note = DailyNote.query.get_or_404(note_id)

    if note.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'msg': '无权删除'}), 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({'msg': '日记已删除'}), 200
