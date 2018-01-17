# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 10:23
# @Author  : caoshuai
# @File    : errors.py
# @Software: PyCharm

from . import api
from flask import jsonify,request,render_template

@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response

def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response
