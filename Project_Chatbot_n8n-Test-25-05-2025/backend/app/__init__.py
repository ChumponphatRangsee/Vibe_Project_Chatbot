from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db, migrate
from .general_routes import bp, api_routes
from app.routes.product_routes import product_bp, klevu_service


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, origins=["http://localhost:3000"])

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Klevu service with app config
    klevu_service.init_app(app)

    # Create tables within app context
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(api_routes)
    app.register_blueprint(bp)
    app.register_blueprint(product_bp, url_prefix='/api/products')
    
    return app

