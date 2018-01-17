# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 16:38
# @Author  : caoshuai
# @File    : __init__.py.py
# @Software: PyCharm Community Edition

from flask import Blueprint

api = Blueprint('api', __name__)
from . import assets,authentication,tasks,dockers