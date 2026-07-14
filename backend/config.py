import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sweet-kitchen-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-sweet-kitchen-secret')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 7  # 7 days
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Upload paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    UPLOAD_DISHES = os.path.join(BASE_DIR, 'uploads', 'dishes')
    UPLOAD_AVATARS = os.path.join(BASE_DIR, 'uploads', 'avatars')
    UPLOAD_STORE = os.path.join(BASE_DIR, 'uploads', 'store')
    UPLOAD_DIARY = os.path.join(BASE_DIR, 'uploads', 'diary')

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "sweet_kitchen.db")}'
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
