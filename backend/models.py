"""Database models for Sweet Kitchen v2."""

from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


# ---------------------------------------------------------------------------
# v1 models (updated)
# ---------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(80), default='')
    balance = db.Column(db.Integer, default=0)  # cents
    role = db.Column(db.String(20), default='customer')
    avatar = db.Column(db.String(256), default='')
    favorite_dish_ids = db.Column(db.Text, default='[]')  # JSON array of dish IDs
    badge_title = db.Column(db.String(50), default='')      # selected achievement title
    wish_coins = db.Column(db.Integer, default=3)            # monthly wish coins
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='user', lazy='dynamic',
                             foreign_keys='Order.user_id')
    balance_logs = db.relationship('BalanceLog', backref='user', lazy='dynamic',
                                   order_by='BalanceLog.created_at.desc()')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    daily_photos = db.relationship('DailyPhoto', backref='user', lazy='dynamic')
    daily_notes = db.relationship('DailyNote', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'balance': self.balance,
            'role': self.role,
            'avatar': self.avatar,
            'favorite_dish_ids': self.favorite_dish_ids,
            'badge_title': self.badge_title,
            'wish_coins': self.wish_coins,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class DishCategory(db.Model):
    __tablename__ = 'dish_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(10), default='🍽️')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dishes = db.relationship('Dish', backref='category', lazy='dynamic',
                             order_by='Dish.sort_order')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'dish_count': self.dishes.filter_by(is_available=True).count(),
        }


class Dish(db.Model):
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('dish_categories.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(256), default='')
    description = db.Column(db.Text, default='')
    note = db.Column(db.String(20), default='')          # v2: short note
    sold_count = db.Column(db.Integer, default=0)         # v2: sales count
    ingredients = db.Column(db.Text, default='')           # v2: ingredient list
    is_available = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    images = db.relationship('DishImage', backref='dish', lazy='joined',
                             order_by='DishImage.sort_order',
                             cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='dish', lazy='dynamic')

    @property
    def avg_rating(self):
        result = db.session.query(
            db.func.avg(Review.rating)
        ).filter(Review.dish_id == self.id).scalar()
        return round(float(result), 1) if result else 0

    @property
    def review_count(self):
        return self.reviews.count()

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'category_icon': self.category.icon if self.category else '',
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'images': [img.to_dict() for img in self.images],
            'description': self.description,
            'note': self.note,
            'sold_count': self.sold_count,
            'ingredients': self.ingredients,
            'avg_rating': self.avg_rating,
            'review_count': self.review_count,
            'is_available': self.is_available,
            'sort_order': self.sort_order,
        }


class DishImage(db.Model):
    """Multiple images per dish."""
    __tablename__ = 'dish_images'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    image = db.Column(db.String(256), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'image': self.image,
            'sort_order': self.sort_order,
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    placed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # v2
    chef_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # v2
    meal_type = db.Column(db.String(20), default='')  # v2: breakfast/lunch/dinner/snack/night_snack
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    estimated_time = db.Column(db.DateTime, nullable=True)  # v2
    note = db.Column(db.Text, default='')
    mood = db.Column(db.String(10), default='')      # v2
    mood_note = db.Column(db.Text, default='')        # v2
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    items = db.relationship('OrderItem', backref='order', lazy='joined',
                            cascade='all, delete-orphan')

    def to_dict(self, include_items=True):
        # Resolve related users
        placer = db.session.get(User, self.placed_by) if self.placed_by else None
        chef = db.session.get(User, self.chef_user_id) if self.chef_user_id else None

        data = {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'placed_by': self.placed_by,
            'placed_by_nickname': placer.nickname if placer else '',
            'chef_user_id': self.chef_user_id,
            'chef_nickname': chef.nickname if chef else '',
            'meal_type': self.meal_type,
            'order_no': self.order_no,
            'total_amount': self.total_amount,
            'status': self.status,
            'estimated_time': self.estimated_time.isoformat() if self.estimated_time else None,
            'note': self.note,
            'mood': self.mood,
            'mood_note': self.mood_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
            data['item_count'] = sum(item.quantity for item in self.items)
        return data


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    dish_name = db.Column(db.String(120), nullable=False)
    dish_image = db.Column(db.String(256), default='')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'dish_name': self.dish_name,
            'dish_image': self.dish_image,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.price * self.quantity,
        }


class BalanceLog(db.Model):
    __tablename__ = 'balance_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)
    ref_id = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'action': self.action,
            'ref_id': self.ref_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# v2 new models
# ---------------------------------------------------------------------------

class Review(db.Model):
    """Dish review with star rating and admin reply."""
    __tablename__ = 'reviews'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'dish_id', name='uq_user_dish_review'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    content = db.Column(db.Text, default='')
    reply = db.Column(db.Text, default='')           # admin reply
    replied_at = db.Column(db.DateTime, nullable=True)  # when admin replied
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'user_avatar': self.user.avatar if self.user else '',
            'dish_id': self.dish_id,
            'rating': self.rating,
            'content': self.content,
            'reply': self.reply,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class StoreConfig(db.Model):
    """Key-value store for shop configuration."""
    __tablename__ = 'store_config'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text, default='')

    def to_dict(self):
        return {'key': self.key, 'value': self.value}


class DailyPhoto(db.Model):
    """Photos uploaded to shared diary."""
    __tablename__ = 'daily_photos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    image_path = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'date': self.date.isoformat() if self.date else None,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class DailyNote(db.Model):
    """Diary entries in shared diary."""
    __tablename__ = 'daily_notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    content = db.Column(db.Text, default='')
    mood = db.Column(db.String(10), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'date': self.date.isoformat() if self.date else None,
            'content': self.content,
            'mood': self.mood,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TodaySpecial(db.Model):
    """Admin's daily special dish."""
    __tablename__ = 'today_special'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    date = db.Column(db.Date, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dish = db.relationship('Dish', backref='today_specials')

    def to_dict(self):
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'dish': self.dish.to_dict() if self.dish else None,
            'date': self.date.isoformat() if self.date else None,
        }


class Wish(db.Model):
    """Wishing pool - users suggest dishes they want."""
    __tablename__ = 'wishes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')  # pending | fulfilled
    likes = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)                 # total coins invested
    is_anonymous = db.Column(db.Boolean, default=False)      # anonymous wish
    fulfill_note = db.Column(db.Text, default='')            # admin note on fulfill
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='wishes')

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'title': self.title, 'description': self.description,
            'status': self.status, 'likes': self.likes,
            'coins': self.coins, 'is_anonymous': self.is_anonymous,
            'fulfill_note': self.fulfill_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SpecialDate(db.Model):
    """Memorial dates (birthdays, anniversaries, etc)."""
    __tablename__ = 'special_dates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    icon = db.Column(db.String(10), default='📌')
    repeat_yearly = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date.isoformat() if self.date else None,
            'icon': self.icon,
            'repeat_yearly': self.repeat_yearly,
        }
