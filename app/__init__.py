from flask import Flask
from config import Config
from .db import create_table,create_property_table
from app.extensions import mail

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    create_table()
    create_property_table()
    
    mail.init_app(app)
    
    from .home.routes import home_bp
    app.register_blueprint(home_bp)
    
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from .owner.routes import owner_bp
    app.register_blueprint(owner_bp)
    
    from .buyer.routes import buyer_bp
    app.register_blueprint(buyer_bp)
    
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    
    return app

    
    @app.after_request
    def add_global_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response