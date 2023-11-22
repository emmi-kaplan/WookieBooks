from flask import Flask
from models import db
from config import DevelopmentConfig, ProductionConfig, TestingConfig

def create_app(config_name='development'):
    app = Flask(__name__)

    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize the db with the app
    db.init_app(app)

    # Import and Register Blueprints
    from endpoints.books import books_bp
    books_bp.db = db
    app.register_blueprint(books_bp, url_prefix='/books')

    from endpoints.user import user_bp
    user_bp.db = db
    app.register_blueprint(user_bp, url_prefix='/user')

    from endpoints.auth import auth_bp
    auth_bp.db = db
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Create the tables inside application context
    with app.app_context():
        db.create_all()

    return app
