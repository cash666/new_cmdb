# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 11:37
# @Author  : caoshuai
# @File    : run.py
# @Software: PyCharm Community Edition

from app import app

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)