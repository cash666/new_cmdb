# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 10:42
# @Author  : caoshuai
# @File    : models.py
# @Software: PyCharm Community Edition

from app import db,login_manager
from datetime import datetime
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32))
    password_hash = db.Column(db.String(256))
    email = db.Column(db.String(64))
    status = db.Column(db.Boolean, default = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    create_time = db.Column(db.DateTime, default = datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, passwd):
        self.password_hash = generate_password_hash(passwd)

    def verify_password(self, passwd):
        return check_password_hash(self.password_hash, passwd)

    def uncheck_tasks(self):
        from app.task.models import Task
        if self.role.name == 'admin':
            return Task.query.filter(Task.check_status == u'待审核').count()
        else:
            return Task.query.filter(Task.checker == self.name,Task.check_status == u'待审核').count()

    def unfinish_tasks(self):
        from app.task.models import Task
        if self.role.name == 'admin':
            return Task.query.filter(Task.check_status == u'通过').count()
        else:
            return Task.query.filter(Task.publisher == self.name, Task.check_status == u'通过').count()

    def generate_auth_token(self,expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in = expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key = True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key = True),
)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), unique = True)
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')
    permissions = db.relationship('Permission', secondary = role_permission, backref = db.backref('roles',lazy = 'dynamic'), lazy = 'dynamic')
    create_time = db.Column(db.DateTime, default = datetime.utcnow)

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), unique = True)
    alias_name = db.Column(db.String(32), unique = True)
    create_time = db.Column(db.DateTime, default = datetime.utcnow)

class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))