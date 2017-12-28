# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 11:39
# @Author  : caoshuai
# @File    : resetdb.py
# @Software: PyCharm Community Edition

from app import app,db

with app.app_context():
    db.create_all()