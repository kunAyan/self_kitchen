"""Store config and today special APIs."""

from datetime import date

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from models import StoreConfig, TodaySpecial, Dish
from extensions import db
from api import store_bp


# ---------------------------------------------------------------------------
# Public: store config
# ---------------------------------------------------------------------------

@store_bp.route('/store/config', methods=['GET'])
def get_store_config():
    configs = StoreConfig.query.all()
    result = {}
    for c in configs:
        result[c.key] = c.value
    return jsonify({'config': result}), 200


# ---------------------------------------------------------------------------
# Public: today special
# ---------------------------------------------------------------------------

@store_bp.route('/today-special', methods=['GET'])
def get_today_special():
    special = TodaySpecial.query.filter_by(date=date.today()).first()
    if not special:
        return jsonify({'special': None}), 200
    return jsonify({'special': special.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin: store config
# ---------------------------------------------------------------------------

@store_bp.route('/admin/store/config', methods=['PUT'])
@jwt_required()
def update_store_config():
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'msg': '需要管理员权限'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'msg': '请提供配置数据'}), 400

    for key, value in data.items():
        config = StoreConfig.query.filter_by(key=key).first()
        if config:
            config.value = str(value) if not isinstance(value, str) else value
        else:
            db.session.add(StoreConfig(key=key, value=str(value) if not isinstance(value, str) else value))

    db.session.commit()
    return jsonify({'msg': '配置已更新'}), 200


# ---------------------------------------------------------------------------
# Admin: today special
# ---------------------------------------------------------------------------

@store_bp.route('/admin/today-special', methods=['PUT'])
@jwt_required()
def set_today_special():
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'msg': '需要管理员权限'}), 403

    data = request.get_json()
    dish_id = data.get('dish_id')
    if dish_id is None:
        return jsonify({'msg': '请选择菜品'}), 400

    # Allow clearing (dish_id = 0 or null)
    if dish_id == 0 or dish_id is None:
        today = date.today()
        TodaySpecial.query.filter_by(date=today).delete()
        db.session.commit()
        return jsonify({'msg': '已取消今日特供'}), 200

    dish = db.session.get(Dish, dish_id)
    if not dish:
        return jsonify({'msg': '菜品不存在'}), 404

    today = date.today()
    special = TodaySpecial.query.filter_by(date=today).first()
    if special:
        special.dish_id = dish_id
    else:
        db.session.add(TodaySpecial(dish_id=dish_id, date=today))

    db.session.commit()
    return jsonify({'msg': f'今日特供已设为「{dish.name}」'}), 200
