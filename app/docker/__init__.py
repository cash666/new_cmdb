# -*- coding: utf-8 -*-
# @Time    : 2018/01/02 11:28
# @Author  : caoshuai
# @File    : __init__.py
# @Software: PyCharm Community Edition

from flask import Blueprint

docker = Blueprint('docker', __name__)
from . import views,errors