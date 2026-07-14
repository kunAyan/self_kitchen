"""Admin API - v2: dashboard, users, categories, dishes, orders, special dates."""

from datetime import datetime, date, timedelta, timezone

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from werkzeug.security import generate_password_hash
from models import (User, DishCategory, Dish, DishImage, Order, OrderItem,
                    BalanceLog, Review, StoreConfig, SpecialDate, TodaySpecial)
from extensions import db
from api import admin_bp


def admin_required():
    user = get_current_user()
    if user.role != 'admin':
        return None, jsonify({'msg': '需要管理员权限'}), 403
    return user, None, None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    _, err, code = admin_required()
    if err:
        return err, code

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    customers = User.query.filter_by(role='customer').all()
    pending_orders = Order.query.filter_by(status='pending').count()
    today_orders = Order.query.filter(Order.created_at >= today_start).count()
    total_dishes = Dish.query.filter_by(is_available=True).count()

    return jsonify({
        'stats': {
            'customers': [u.to_dict() for u in customers],
            'total_dishes': total_dishes,
            'pending_orders': pending_orders,
            'today_orders': today_orders,
        },
    }), 200


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    _, err, code = admin_required()
    if err:
        return err, code

    users = User.query.filter_by(role='customer').order_by(User.id).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    _, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'msg': '用户名和密码不能为空'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': '用户名已存在'}), 409

    user = User(
        username=username,
        nickname=data.get('nickname', username),
        role='customer',
        balance=data.get('balance', 0),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'user': user.to_dict()}), 201


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    _, err, code = admin_required()
    if err:
        return err, code

    target = db.session.get(User, user_id)
    if not target:
        return jsonify({'msg': '用户不存在'}), 404

    logs = BalanceLog.query.filter_by(user_id=user_id) \
        .order_by(BalanceLog.created_at.desc()).limit(30).all()

    return jsonify({
        'user': target.to_dict(),
        'balance_logs': [log.to_dict() for log in logs],
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Edit user: nickname, password, balance."""
    _, err, code = admin_required()
    if err:
        return err, code

    target = db.session.get(User, user_id)
    if not target:
        return jsonify({'msg': '用户不存在'}), 404

    data = request.get_json()
    if data.get('nickname'):
        target.nickname = data['nickname'].strip()
    if data.get('password'):
        target.password_hash = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({'user': target.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>/balance', methods=['PUT'])
@jwt_required()
def adjust_balance(user_id):
    """Adjust balance. Body: {amount: 1000} positive=add, negative=deduct."""
    _, err, code = admin_required()
    if err:
        return err, code

    target = db.session.get(User, user_id)
    if not target:
        return jsonify({'msg': '用户不存在'}), 404

    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'msg': '请提供金额（单位：分）'}), 400

    amount = data['amount']
    if not isinstance(amount, int) or amount == 0:
        return jsonify({'msg': '金额必须是非零整数（单位：分）'}), 400

    target.balance += amount
    db.session.add(BalanceLog(
        user_id=target.id,
        amount=amount,
        balance_after=target.balance,
        action='admin_topup' if amount > 0 else 'admin_deduct',
    ))
    db.session.commit()

    return jsonify({
        'user': target.to_dict(),
        'msg': f'余额已更新：¥{target.balance/100:.2f}',
    }), 200


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@admin_bp.route('/categories', methods=['GET'])
@jwt_required()
def list_categories():
    _, err, code = admin_required()
    if err:
        return err, code

    categories = DishCategory.query.order_by(DishCategory.sort_order).all()
    return jsonify({'categories': [
        {**c.to_dict(), 'dish_count': c.dishes.count()} for c in categories
    ]}), 200


@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    _, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    if not data or not data.get('name', '').strip():
        return jsonify({'msg': '分类名称不能为空'}), 400

    cat = DishCategory(
        name=data['name'].strip(),
        icon=data.get('icon', '🍽️'),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'category': cat.to_dict()}), 201


@admin_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@jwt_required()
def update_category(cat_id):
    _, err, code = admin_required()
    if err:
        return err, code

    cat = db.session.get(DishCategory, cat_id)
    if not cat:
        return jsonify({'msg': '分类不存在'}), 404

    data = request.get_json()
    if data:
        if 'name' in data:
            cat.name = data['name'].strip() or cat.name
        if 'icon' in data:
            cat.icon = data['icon']
        if 'sort_order' in data:
            cat.sort_order = data['sort_order']
    db.session.commit()
    return jsonify({'category': cat.to_dict()}), 200


@admin_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_category(cat_id):
    _, err, code = admin_required()
    if err:
        return err, code

    cat = db.session.get(DishCategory, cat_id)
    if not cat:
        return jsonify({'msg': '分类不存在'}), 404
    if cat.dishes.count() > 0:
        return jsonify({'msg': '该分类下还有菜品，请先删除或移动菜品'}), 400

    db.session.delete(cat)
    db.session.commit()
    return jsonify({'msg': '删除成功'}), 200


# ---------------------------------------------------------------------------
# Dishes
# ---------------------------------------------------------------------------

@admin_bp.route('/dishes', methods=['GET'])
@jwt_required()
def list_dishes():
    _, err, code = admin_required()
    if err:
        return err, code

    category_id = request.args.get('category_id', type=int)
    query = Dish.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    dishes = query.order_by(Dish.category_id, Dish.sort_order, Dish.id).all()
    return jsonify({'dishes': [d.to_dict() for d in dishes]}), 200


@admin_bp.route('/dishes', methods=['POST'])
@jwt_required()
def create_dish():
    _, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({'msg': '请提供菜品信息'}), 400

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'msg': '菜品名称不能为空'}), 400

    price = data.get('price', 0)
    if not isinstance(price, int) or price <= 0:
        return jsonify({'msg': '价格必须是大于0的整数（单位：分）'}), 400

    category_id = data.get('category_id')
    if not category_id or not db.session.get(DishCategory, category_id):
        return jsonify({'msg': '请选择有效的分类'}), 400

    dish = Dish(
        category_id=category_id,
        name=name, price=price,
        image=data.get('image', ''),
        description=data.get('description', ''),
        note=data.get('note', '')[:20],
        is_available=data.get('is_available', True),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(dish)
    db.session.flush()

    # Add extra images
    images = data.get('images', [])
    for i, img in enumerate(images):
        db.session.add(DishImage(dish_id=dish.id, image=img, sort_order=i + 1))

    db.session.commit()
    return jsonify({'dish': dish.to_dict()}), 201


@admin_bp.route('/dishes/<int:dish_id>', methods=['PUT'])
@jwt_required()
def update_dish(dish_id):
    _, err, code = admin_required()
    if err:
        return err, code

    dish = db.session.get(Dish, dish_id)
    if not dish:
        return jsonify({'msg': '菜品不存在'}), 404

    data = request.get_json()
    if data:
        for field in ['name', 'price', 'category_id', 'image', 'description',
                       'note', 'is_available', 'sort_order']:
            if field in data:
                val = data[field]
                if field == 'name':
                    val = val.strip() or dish.name
                if field == 'note':
                    val = (val or '')[:20]
                setattr(dish, field, val)

        # Update extra images
        if 'images' in data:
            DishImage.query.filter_by(dish_id=dish.id).delete()
            for i, img in enumerate(data['images']):
                db.session.add(DishImage(dish_id=dish.id, image=img, sort_order=i + 1))

    db.session.commit()
    return jsonify({'dish': dish.to_dict()}), 200


@admin_bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
@jwt_required()
def delete_dish(dish_id):
    """Soft delete: mark unavailable. Only hard delete if not referenced."""
    _, err, code = admin_required()
    if err:
        return err, code

    dish = db.session.get(Dish, dish_id)
    if not dish:
        return jsonify({'msg': '菜品不存在'}), 404

    from models import OrderItem
    ref_count = OrderItem.query.filter_by(dish_id=dish_id).count()
    if ref_count > 0:
        dish.is_available = False
        db.session.commit()
        return jsonify({'msg': '该菜品有历史订单，已下架处理'}), 200

    db.session.delete(dish)
    db.session.commit()
    return jsonify({'msg': '删除成功'}), 200


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def list_orders_admin():
    _, err, code = admin_required()
    if err:
        return err, code

    query = Order.query
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict(include_items=False) for o in orders]}), 200


@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_admin(order_id):
    _, err, code = admin_required()
    if err:
        return err, code

    order = Order.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()}), 200


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    _, err, code = admin_required()
    if err:
        return err, code

    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'msg': '请提供新状态'}), 400

    new_status = data['status']
    valid = {
        'pending': ['accepted', 'rejected'],
        'accepted': ['completed'],
    }
    if new_status not in valid.get(order.status, []):
        return jsonify({'msg': f'不能将订单从「{order.status}」改为「{new_status}」'}), 400

    try:
        if new_status == 'rejected':
            balance_user = db.session.get(User, order.placed_by) if order.placed_by else db.session.get(User, order.user_id)
            balance_user.balance += order.total_amount
            db.session.add(BalanceLog(
                user_id=balance_user.id,
                amount=order.total_amount,
                balance_after=balance_user.balance,
                action='order_refund',
                ref_id=order.id,
            ))

        if new_status == 'accepted' and data.get('estimated_time'):
            from datetime import datetime as dt
            order.estimated_time = dt.fromisoformat(data['estimated_time'])

        order.status = new_status
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'msg': '操作失败，请重试'}), 500

    return jsonify({'order': order.to_dict()}), 200


# ---------------------------------------------------------------------------
# Special dates
# ---------------------------------------------------------------------------

@admin_bp.route('/special-dates', methods=['GET'])
@jwt_required()
def list_special_dates():
    _, err, code = admin_required()
    if err:
        return err, code

    dates = SpecialDate.query.order_by(
        db.func.strftime('%m-%d', SpecialDate.date)
    ).all()
    return jsonify({'special_dates': [d.to_dict() for d in dates]}), 200


@admin_bp.route('/special-dates', methods=['POST'])
@jwt_required()
def create_special_date():
    _, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    if not data or not data.get('title') or not data.get('date'):
        return jsonify({'msg': '请填写标题和日期'}), 400

    try:
        d = date.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'msg': '日期格式错误'}), 400

    sd = SpecialDate(
        title=data['title'],
        date=d,
        icon=data.get('icon', '📌'),
        repeat_yearly=data.get('repeat_yearly', False),
    )
    db.session.add(sd)
    db.session.commit()
    return jsonify({'special_date': sd.to_dict()}), 201


@admin_bp.route('/special-dates/<int:sd_id>', methods=['PUT'])
@jwt_required()
def update_special_date(sd_id):
    _, err, code = admin_required()
    if err:
        return err, code

    sd = db.session.get(SpecialDate, sd_id)
    if not sd:
        return jsonify({'msg': '不存在'}), 404

    data = request.get_json()
    if data:
        if 'title' in data:
            sd.title = data['title']
        if 'date' in data:
            sd.date = date.fromisoformat(data['date'])
        if 'icon' in data:
            sd.icon = data['icon']
        if 'repeat_yearly' in data:
            sd.repeat_yearly = data['repeat_yearly']
    db.session.commit()
    return jsonify({'special_date': sd.to_dict()}), 200


@admin_bp.route('/special-dates/<int:sd_id>', methods=['DELETE'])
@jwt_required()
def delete_special_date(sd_id):
    _, err, code = admin_required()
    if err:
        return err, code

    sd = db.session.get(SpecialDate, sd_id)
    if not sd:
        return jsonify({'msg': '不存在'}), 404

    db.session.delete(sd)
    db.session.commit()
    return jsonify({'msg': '删除成功'}), 200


# ---------------------------------------------------------------------------
# Batch dish operations
# ---------------------------------------------------------------------------

@admin_bp.route('/dishes/batch', methods=['PUT'])
@jwt_required()
def batch_update_dishes():
    """Batch update dishes: toggle availability or adjust prices."""
    _, err, code = admin_required()
    if err:
        return err, code

    data = request.get_json()
    dish_ids = data.get('ids', [])
    action = data.get('action', '')  # 'toggle_available', 'set_price', 'mark_unavailable'
    value = data.get('value')        # for set_price: new price in cents

    if not dish_ids:
        return jsonify({'msg': '请选择菜品'}), 400

    dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
    if not dishes:
        return jsonify({'msg': '未找到菜品'}), 404

    count = 0
    for dish in dishes:
        if action == 'toggle_available':
            dish.is_available = not dish.is_available
            count += 1
        elif action == 'mark_available':
            dish.is_available = True
            count += 1
        elif action == 'mark_unavailable':
            dish.is_available = False
            count += 1
        elif action == 'set_price' and value is not None:
            if isinstance(value, int) and value > 0:
                dish.price = value
                count += 1

    db.session.commit()
    return jsonify({'msg': f'已更新 {count} 个菜品', 'count': count}), 200


# ---------------------------------------------------------------------------
# Review reply
# ---------------------------------------------------------------------------

@admin_bp.route('/reviews/<int:review_id>/reply', methods=['PUT'])
@jwt_required()
def reply_review(review_id):
    """Admin reply to a review."""
    _, err, code = admin_required()
    if err:
        return err, code

    review = Review.query.get_or_404(review_id)
    data = request.get_json()
    review.reply = data.get('reply', '').strip()
    review.replied_at = datetime.now(timezone.utc) if review.reply else None
    db.session.commit()
    return jsonify({'review': review.to_dict()}), 200


# ---------------------------------------------------------------------------
# Sales stats
# ---------------------------------------------------------------------------

@admin_bp.route('/sales-stats', methods=['GET'])
@jwt_required()
def sales_stats():
    """Get sales statistics for admin dashboard."""
    _, err, code = admin_required()
    if err:
        return err, code

    # Top dishes by sales
    top_dishes = Dish.query.filter(Dish.sold_count > 0) \
        .order_by(Dish.sold_count.desc()).limit(10).all()

    # Orders by meal_type
    from sqlalchemy import func
    meal_stats = db.session.query(
        Order.meal_type, func.count(Order.id), func.sum(Order.total_amount)
    ).filter(Order.meal_type != '').group_by(Order.meal_type).all()

    # Monthly totals (last 6 months)
    monthly = []
    for i in range(5, -1, -1):
        now = datetime.utcnow()
        y, m = now.year, now.month
        m -= i
        while m <= 0:
            m += 12; y -= 1
        start = datetime(y, m, 1)
        if m == 12:
            end = datetime(y + 1, 1, 1)
        else:
            end = datetime(y, m + 1, 1)
        count = Order.query.filter(
            Order.created_at >= start, Order.created_at < end
        ).count()
        total = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start, Order.created_at < end
        ).scalar() or 0
        monthly.append({'year': y, 'month': m, 'count': count, 'total': total})

    return jsonify({
        'top_dishes': [d.to_dict() for d in top_dishes],
        'meal_stats': [{'type': t, 'count': c, 'total': int(s or 0)} for t, c, s in meal_stats],
        'monthly': monthly,
    }), 200


# ---------------------------------------------------------------------------
# Monthly report
# ---------------------------------------------------------------------------

@admin_bp.route('/monthly-report', methods=['GET'])
@jwt_required()
def monthly_report():
    """Generate a monthly family dining report."""
    _, err, code = admin_required()
    if err:
        return err, code

    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)

    orders = Order.query.filter(Order.created_at >= start).all()
    total_amount = sum(o.total_amount for o in orders)
    total_count = len(orders)

    # Most ordered dish this month
    from models import OrderItem
    dish_counts = {}
    for o in orders:
        for item in o.items:
            dish_counts[item.dish_name] = dish_counts.get(item.dish_name, 0) + item.quantity
    top_dish = max(dish_counts, key=dish_counts.get) if dish_counts else None

    # Most active chef
    chef_counts = {}
    for o in orders:
        if o.chef_user_id:
            chef = db.session.get(User, o.chef_user_id)
            name = chef.nickname if chef else '未知'
            chef_counts[name] = chef_counts.get(name, 0) + 1
    top_chef = max(chef_counts, key=chef_counts.get) if chef_counts else None

    # New reviews
    new_reviews = Review.query.filter(Review.created_at >= start).count()

    return jsonify({
        'report': {
            'year': now.year, 'month': now.month,
            'total_orders': total_count,
            'total_amount': total_amount,
            'top_dish': top_dish,
            'top_dish_count': dish_counts.get(top_dish, 0) if top_dish else 0,
            'top_chef': top_chef,
            'top_chef_count': chef_counts.get(top_chef, 0) if top_chef else 0,
            'new_reviews': new_reviews,
            'active_users': User.query.filter_by(role='customer').count(),
        },
    }), 200
