"""Orders API - create, list, detail, cancel, mood."""

from datetime import datetime, timezone
from random import randint

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from models import User, Dish, Order, OrderItem, BalanceLog
from extensions import db
from api import orders_bp


@orders_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    current_user = get_current_user()
    data = request.get_json()

    if not data or 'items' not in data or not data['items']:
        return jsonify({'msg': '订单至少需要一个菜品'}), 400

    # Determine order ownership and balance source
    # Admin orders are assigned to lqyispig (the girlfriend)
    gf = User.query.filter_by(username='lqyispig').first()
    if current_user.role == 'admin' and gf:
        order_user = gf        # order appears in gf's list
        placed_by = current_user.id
        balance_user = current_user  # deduct from admin
    else:
        order_user = current_user
        placed_by = None
        balance_user = current_user

    # Validate dishes and calculate total
    total = 0
    order_items_data = []
    for item in data['items']:
        dish_id = item.get('dish_id')
        quantity = item.get('quantity', 1)
        if quantity < 1:
            return jsonify({'msg': '菜品数量不能小于1'}), 400

        dish = db.session.get(Dish, dish_id)
        if not dish:
            return jsonify({'msg': f'菜品不存在 (id={dish_id})'}), 404
        if not dish.is_available:
            return jsonify({'msg': f'「{dish.name}」已下架'}), 400

        line_total = dish.price * quantity
        total += line_total
        order_items_data.append({
            'dish_id': dish.id, 'dish_name': dish.name,
            'dish_image': dish.image, 'quantity': quantity, 'price': dish.price,
        })

    # Check balance
    if balance_user.balance < total:
        shortage = total - balance_user.balance
        return jsonify({
            'msg': f'余额不足！还差 ¥{shortage/100:.2f}',
            'balance': balance_user.balance, 'required': total,
        }), 400

    # Generate order number
    now = datetime.now(timezone.utc)
    order_no = now.strftime('%Y%m%d%H%M%S') + f'{randint(100, 999)}'

    # v2 fields
    chef_user_id = data.get('chef_user_id')
    meal_type = data.get('meal_type', '')

    try:
        balance_user.balance -= total

        order = Order(
            user_id=order_user.id,
            placed_by=placed_by,
            chef_user_id=chef_user_id,
            meal_type=meal_type,
            order_no=order_no,
            total_amount=total,
            status='pending',
            note=data.get('note', ''),
        )
        db.session.add(order)
        db.session.flush()

        for item_data in order_items_data:
            db.session.add(OrderItem(order_id=order.id, **item_data))

        # Update sold_count
        for item in order_items_data:
            dish = db.session.get(Dish, item['dish_id'])
            if dish:
                dish.sold_count = (dish.sold_count or 0) + item['quantity']

        db.session.add(BalanceLog(
            user_id=balance_user.id,
            amount=-total,
            balance_after=balance_user.balance,
            action='order_payment',
            ref_id=order.id,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'msg': '下单失败，请重试'}), 500

    return jsonify({'order': order.to_dict()}), 201


@orders_bp.route('/orders', methods=['GET'])
@jwt_required()
def list_orders():
    current_user = get_current_user()
    # Show orders where user is the owner OR the placer (for admin who orders for gf)
    from sqlalchemy import or_
    query = Order.query.filter(
        or_(Order.user_id == current_user.id, Order.placed_by == current_user.id)
    )

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict(include_items=False) for o in orders]}), 200


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user = get_current_user()
    order = Order.query.get_or_404(order_id)

    if current_user.role != 'admin' and order.user_id != current_user.id:
        return jsonify({'msg': '无权查看此订单'}), 403

    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/orders/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    current_user = get_current_user()
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id and order.placed_by != current_user.id and current_user.role != 'admin':
        return jsonify({'msg': '无权操作此订单'}), 403
    if order.status != 'pending':
        return jsonify({'msg': '只能取消待处理的订单'}), 400

    # Determine who paid
    balance_user = db.session.get(User, order.placed_by) if order.placed_by else db.session.get(User, order.user_id)

    try:
        balance_user.balance += order.total_amount
        order.status = 'cancelled'
        db.session.add(BalanceLog(
            user_id=balance_user.id,
            amount=order.total_amount,
            balance_after=balance_user.balance,
            action='order_refund',
            ref_id=order.id,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'msg': '取消订单失败，请重试'}), 500

    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/orders/<int:order_id>/mood', methods=['PUT'])
@jwt_required()
def record_mood(order_id):
    """Record post-meal mood."""
    current_user = get_current_user()
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id and order.placed_by != current_user.id and current_user.role != 'admin':
        return jsonify({'msg': '无权操作此订单'}), 403
    if order.status != 'completed':
        return jsonify({'msg': '只能为已完成的订单记录心情'}), 400

    data = request.get_json()
    order.mood = data.get('mood', '')
    order.mood_note = data.get('mood_note', '')
    db.session.commit()

    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/balance/logs', methods=['GET'])
@jwt_required()
def balance_logs():
    current_user = get_current_user()
    logs = BalanceLog.query.filter_by(user_id=current_user.id) \
        .order_by(BalanceLog.created_at.desc()).limit(50).all()
    return jsonify({'logs': [log.to_dict() for log in logs]}), 200
