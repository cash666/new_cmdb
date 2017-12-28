# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 9:29
# @Author  : caoshuai
# @File    : __init__.py.py
# @Software: PyCharm Community Edition

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .task import task as task_blueprint
app.register_blueprint(task_blueprint)

from .asset import asset as asset_blueprint
app.register_blueprint(asset_blueprint)
