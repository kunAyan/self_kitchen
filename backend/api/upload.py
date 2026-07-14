"""File upload API - dishes, avatars, store."""

import os
import uuid

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from api import upload_bp
from config import Config


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_upload(file, subfolder):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    folder = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return f'{subfolder}/{filename}'


@upload_bp.route('/upload/image', methods=['POST'])
@jwt_required()
def upload_dish_image():
    """Upload dish image (admin only)."""
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'msg': '需要管理员权限'}), 403

    if 'file' not in request.files:
        return jsonify({'msg': '请选择文件'}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'msg': f'不支持的图片格式'}), 400

    path = save_upload(file, 'dishes')
    return jsonify({'filename': path, 'url': f'/uploads/{path}'}), 201


@upload_bp.route('/upload/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar."""
    user = get_current_user()

    if 'file' not in request.files:
        return jsonify({'msg': '请选择文件'}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'msg': '不支持的图片格式'}), 400

    path = save_upload(file, 'avatars')
    user.avatar = path
    from extensions import db
    db.session.commit()

    return jsonify({'filename': path, 'url': f'/uploads/{path}'}), 201


@upload_bp.route('/upload/store', methods=['POST'])
@jwt_required()
def upload_store_image():
    """Upload store/banner image (admin only)."""
    user = get_current_user()
    if user.role != 'admin':
        return jsonify({'msg': '需要管理员权限'}), 403

    if 'file' not in request.files:
        return jsonify({'msg': '请选择文件'}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'msg': '不支持的图片格式'}), 400

    img_type = request.form.get('type', 'store')
    path = save_upload(file, img_type)
    return jsonify({'filename': path, 'url': f'/uploads/{path}'}), 201
