"""Dishes API - categories, listing, detail, popular."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from models import DishCategory, Dish
from api import dishes_bp


@dishes_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = DishCategory.query.order_by(DishCategory.sort_order).all()
    return jsonify({'categories': [c.to_dict() for c in categories]}), 200


@dishes_bp.route('/dishes/popular', methods=['GET'])
@jwt_required()
def get_popular_dishes():
    """Get top popular dishes by sold_count."""
    dishes = Dish.query.filter_by(is_available=True) \
        .order_by(Dish.sold_count.desc()).limit(3).all()
    return jsonify({'dishes': [d.to_dict() for d in dishes]}), 200


@dishes_bp.route('/dishes', methods=['GET'])
@jwt_required()
def get_dishes():
    query = Dish.query
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)

    available = request.args.get('available')
    if available is not None:
        query = query.filter_by(is_available=available.lower() == 'true')
    elif not category_id:
        query = query.filter_by(is_available=True)

    dishes = query.order_by(Dish.sort_order, Dish.id).all()
    return jsonify({'dishes': [d.to_dict() for d in dishes]}), 200


@dishes_bp.route('/dishes/<int:dish_id>', methods=['GET'])
@jwt_required()
def get_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    return jsonify({'dish': dish.to_dict()}), 200
