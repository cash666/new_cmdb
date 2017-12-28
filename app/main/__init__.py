# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 16:38
# @Author  : caoshuai
# @File    : __init__.py.py
# @Software: PyCharm Community Edition

from flask import Blueprint

main = Blueprint('main', __name__)
from . import views