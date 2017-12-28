# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 11:40
# @Author  : caoshuai
# @File    : models.py
# @Software: PyCharm Community Edition

from app import db
from datetime import datetime

class AssetGroup(db.Model):
    __tablename__ = 'asset_groups'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32))
    comment = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default = datetime.utcnow)

    def count_assets(self):
        return self.assets.count()

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key = True)
    hostname = db.Column(db.String(32))
    innerIP = db.Column(db.String(32))
    outerIP = db.Column(db.String(32))
    os = db.Column(db.String(32))
    cpu = db.Column(db.String(32))
    memory = db.Column(db.String(32))
    disk = db.Column(db.String(64))
    sn = db.Column(db.String(32))
    type = db.Column(db.String(32))
    manufacturer = db.Column(db.String(16))
    model = db.Column(db.String(32))
    asset_number = db.Column(db.String(32))
    cabinet_number = db.Column(db.String(32))
    cabinet_position = db.Column(db.String(32))
    is_online = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(16))
    manager = db.Column(db.String(32))
    applications = db.Column(db.String(128))
    comment = db.Column(db.Text)
    asset_groups = db.relationship('AssetGroup', secondary = "asset_group_relations", backref=db.backref('assets', lazy='dynamic'),lazy='dynamic')
    idc_id = db.Column(db.Integer, db.ForeignKey('idc.id'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_idc(self):
        return self.idc.name

asset_group_relations = db.Table('asset_group_relations',
    db.Column('group_id', db.Integer, db.ForeignKey('asset_groups.id'), primary_key = True),
    db.Column('asset_id', db.Integer, db.ForeignKey('assets.id'), primary_key = True),
)

class IDC(db.Model):
    __tablename__ = 'idc'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32))
    bandwidth = db.Column(db.String(16))
    contacts = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    address = db.Column(db.String(32))
    network = db.Column(db.String(64))
    operator = db.Column(db.String(16))
    comment = db.Column(db.Text)
    assets = db.relationship('Asset', backref='idc', lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def count_assets(self):
        return self.assets.count()

