from flask import Flask
from flask_login import LoginManager
from config import Config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes import auth, main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app

from app import models