# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 10:44
# @Author  : caoshuai
# @File    : authentication.py
# @Software: PyCharm

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from app.auth.models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(token_or_username, password):
    if not token_or_username:
        g.current_user = AnonymousUser()
        return True
    if not password:
        g.current_user = User.verify_auth_token(token_or_username)
        g.token_userd = True
        return g.current_user is not None
    user = User.query.filter_by(name = token_or_username).first()
    if not user:
        return False
    g.current_user = user
    g.token_userd = False
    return user.verify_password(password)

@api.route('/api/token')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_userd:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token':g.current_user.generate_auth_token(expiration=3600),
        'expiration':3600
    })

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')