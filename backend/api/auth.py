"""Auth API - login, profile. (register removed in v2)."""

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_current_user
from models import User
from extensions import db
from api import auth_bp


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users_public():
    """Public user list (id + nickname only) for chef selection."""
    users = User.query.with_entities(User.id, User.nickname, User.role).all()
    return jsonify({
        'users': [{'id': u.id, 'nickname': u.nickname, 'role': u.role} for u in users],
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'msg': '请提供登录信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'msg': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'msg': '用户名或密码错误'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user = get_current_user()
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = get_current_user()
    data = request.get_json()
    if data:
        if 'nickname' in data:
            user.nickname = data['nickname'].strip() or user.nickname
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'favorite_dish_ids' in data:
            import json
            user.favorite_dish_ids = json.dumps(data['favorite_dish_ids'])
        if 'badge_title' in data:
            user.badge_title = data['badge_title']
        db.session.commit()
    return jsonify({'user': user.to_dict()}), 200
