# -*- coding: utf-8 -*-
# @Time    : 2018/01/02 11:30
# @Author  : caoshuai
# @File    : models.py
# @Software: PyCharm Community Edition

from app import db
from datetime import datetime

class DockerFile(db.Model):
    __tablename__ = 'docker_files'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32),unique = True)
    path = db.Column(db.String(32),unique = True)
    content = db.Column(db.Text)
    description = db.Column(db.Text)
    creater = db.Column(db.String(16))
    images = db.relationship('DockerImage', backref='dockerfile', lazy='dynamic')
    create_time = db.Column(db.DateTime, default = datetime.utcnow)

class DockerImage(db.Model):
    __tablename__ = 'docker_images'

    id = db.Column(db.Integer, primary_key = True)
    image_name = db.Column(db.String(32))
    tag_name = db.Column(db.String(32))
    image_id = db.Column(db.String(32))
    creater = db.Column(db.String(16))
    dockerfile_id = db.Column(db.Integer, db.ForeignKey('docker_files.id'))
    containers = db.relationship('DockerContainer', backref='image', lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

class DockerContainer(db.Model):
    __tablename__ = 'docker_containers'

    id = db.Column(db.Integer, primary_key = True)
    container_name = db.Column(db.String(32))
    container_id = db.Column(db.String(32))
    status = db.Column(db.Boolean, default = False)
    src_port = db.Column(db.String(32))
    dst_port = db.Column(db.String(32))
    image_id = db.Column(db.Integer, db.ForeignKey('docker_images.id'))
    creater = db.Column(db.String(16))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
