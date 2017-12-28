# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 9:56
# @Author  : caoshuai
# @File    : __init__.py
# @Software: PyCharm Community Edition

from flask import Blueprint

asset = Blueprint('asset', __name__)
from . import views,errors