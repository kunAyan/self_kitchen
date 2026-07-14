"""API blueprint registration."""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dishes_bp = Blueprint('dishes', __name__)
orders_bp = Blueprint('orders', __name__)
admin_bp = Blueprint('admin', __name__)
upload_bp = Blueprint('upload', __name__)
store_bp = Blueprint('store', __name__)        # v2
diary_bp = Blueprint('diary', __name__)         # v2


def register_blueprints(app):
    from api import auth, dishes, orders, admin, upload  # noqa: F401
    from api import store, diary, reviews  # noqa: F401  # v2

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dishes_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(store_bp, url_prefix='/api')    # v2
    app.register_blueprint(diary_bp, url_prefix='/api')    # v2
