from flask import Flask
from app.config import Config
from app.database import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Database Initialization Hook inside Context
    with app.app_context():
        init_db()

    # Dynamic Blueprint Route Bindings
    from app.routes import main as main_bp
    app.register_blueprint(main_bp)

    return app