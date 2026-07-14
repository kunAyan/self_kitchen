"""Reviews API."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_current_user
from models import Review, Dish, Order
from extensions import db
from api import dishes_bp as bp


@bp.route('/dishes/<int:dish_id>/reviews', methods=['GET'])
@jwt_required()
def list_reviews(dish_id):
    dish = db.session.get(Dish, dish_id)
    if not dish:
        return jsonify({'msg': '菜品不存在'}), 404

    reviews = Review.query.filter_by(dish_id=dish_id) \
        .order_by(Review.created_at.desc()).all()
    return jsonify({
        'reviews': [r.to_dict() for r in reviews],
        'avg_rating': dish.avg_rating,
        'review_count': dish.review_count,
    }), 200


@bp.route('/dishes/<int:dish_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(dish_id):
    current_user = get_current_user()
    dish = db.session.get(Dish, dish_id)
    if not dish:
        return jsonify({'msg': '菜品不存在'}), 404

    # Check if user has a completed order for this dish
    has_completed = Order.query.filter_by(
        user_id=current_user.id, status='completed'
    ).join(Order.items).filter_by(dish_id=dish_id).first()
    if not has_completed:
        return jsonify({'msg': '只有完成订单后才能评价'}), 403

    # Check existing review
    existing = Review.query.filter_by(user_id=current_user.id, dish_id=dish_id).first()
    if existing:
        return jsonify({'msg': '您已评价过这道菜'}), 409

    data = request.get_json()
    rating = data.get('rating', 0)
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'msg': '评分需为1-5的整数'}), 400

    review = Review(
        user_id=current_user.id,
        dish_id=dish_id,
        rating=rating,
        content=data.get('content', ''),
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'review': review.to_dict()}), 201


@bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    current_user = get_current_user()
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'msg': '无权删除此评价'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'msg': '评价已删除'}), 200
