# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 9:37
# @Author  : caoshuai
# @File    : config.py
# @Software: PyCharm Community Edition

#secret_key
SECRET_KEY = 'r9E53Q6iDPvhdqjep0'

#db
SQLALCHEMY_DATABASE_URI = 'mysql://root:12345@127.0.0.1:3306/cmdb_test'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_POOL_RECYCLE = 3600

#redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 6
REDIS_PASS = ''

#mail
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'xxxx@qq.com'
MAIL_PASSWORD = 'xxxx'
FROM_EMAIL = 'xxxx@qq.com'

#分页
PER_PAGE = 10

#文件上传和下载
UPLOAD_DIR = 'upload'
ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','GIF'])

#资产状态
STATUS_LIST = [u'线上',u'空闲',u'下架',u'报废']
ONLINE_LIST = [u'运行中',u'已停止']

#Docker配置
DOCKERFILE_PATH = "/home/cash/cash"
DOCKER_REGISTRY = "10.1.11.180:5000"
