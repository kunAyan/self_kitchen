"""Wishing pool API."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from models import Wish
from extensions import db
from api import wishes_bp as bp


@bp.route('/wishes', methods=['GET'])
@jwt_required()
def list_wishes():
    category = request.args.get('category', '')
    query = Wish.query
    if category in ('dish', 'free'):
        query = query.filter_by(category=category)
    wishes = query.order_by(
        Wish.priority.desc(),
        Wish.created_at.desc()
    ).all()
    return jsonify({'wishes': [w.to_dict() for w in wishes]}), 200


@bp.route('/wishes', methods=['POST'])
@jwt_required()
def create_wish():
    user = get_current_user()
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'msg': '请输入愿望内容'}), 400

    wish = Wish(
        user_id=user.id,
        title=title,
        description=data.get('description', '').strip(),
        category=data.get('category', 'dish'),
        priority=data.get('priority', 2),
    )
    db.session.add(wish)
    db.session.commit()
    return jsonify({'wish': wish.to_dict()}), 201


@bp.route('/wishes/<int:wish_id>', methods=['DELETE'])
@jwt_required()
def delete_wish(wish_id):
    user = get_current_user()
    wish = Wish.query.get_or_404(wish_id)
    if wish.user_id != user.id and user.role != 'admin':
        return jsonify({'msg': '无权删除'}), 403
    db.session.delete(wish)
    db.session.commit()
    return jsonify({'msg': '已删除'}), 200


@bp.route('/admin/wishes/<int:wish_id>/fulfill', methods=['PUT'])
@jwt_required()
def fulfill_wish(wish_id):
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'msg': '需要管理员权限'}), 403

    wish = Wish.query.get_or_404(wish_id)
    data = request.get_json() or {}
    wish.status = 'fulfilled'
    wish.fulfill_note = data.get('note', '')
    db.session.commit()
    return jsonify({'wish': wish.to_dict()}), 200
