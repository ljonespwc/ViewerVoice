from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


# Flask app setup
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or os.urandom(24)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    return app