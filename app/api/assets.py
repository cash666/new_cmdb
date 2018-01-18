# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 14:38
# @Author  : caoshuai
# @File    : assets.py
# @Software: PyCharm

from flask import jsonify,abort,make_response,request,url_for,current_app
from authentication import auth
from . import api
from app import db
from app.asset.models import Asset

@api.route('/api/assets',methods = ['GET'])
@auth.login_required
def get_assets():
    page = request.args.get('page', 1, type=int)
    pagination = Asset.query.paginate(page, per_page=current_app.config['PER_PAGE'],error_out=False)
    assets = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_assets', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_assets', page=page + 1, _external=True)
    asset_list = []
    for asset in assets:
        group_name = ''
        for group in asset.asset_groups.all():
            if group_name:
                group_name = '%s,%s' % (group_name, group.name)
            else:
                group_name = group.name
        asset_list.append({
            'url': url_for('api.get_asset', asset_id = asset.id, _external=True),
            'hostname':asset.hostname,
            'innerIP':asset.innerIP,
            'outerIP':asset.outerIP,
            'os':asset.os,
            'cpu':asset.cpu,
            'memory':asset.memory,
            'disk':asset.disk,
            'sn':asset.sn,
            'type':asset.type,
            'manufacturer':asset.manufacturer,
            'model':asset.model,
            'asset_number':asset.asset_number,
            'cabinet_number':asset.cabinet_number,
            'cabinet_position':asset.cabinet_position,
            'is_online': asset.is_online,
            'status':asset.status,
            'manager':asset.manager,
            'applications':asset.applications,
            'asset_groups':group_name,
            'idc':asset.idc.name,
            'prev': prev,
            'next': next,
            'count': pagination.total,
        })
    return jsonify(asset_list)

@api.route('/api/assets/<int:asset_id>',methods = ['GET'])
@auth.login_required
def get_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if asset is None:
        abort(404)
    group_name = ''
    for group in asset.asset_groups.all():
        if group_name:
            group_name = '%s,%s' % (group_name, group.name)
        else:
            group_name = group.name
    return jsonify({
            'url':url_for('api.get_asset', asset_id = asset_id, _external=True),
            'hostname': asset.hostname,
            'innerIP': asset.innerIP,
            'outerIP': asset.outerIP,
            'os': asset.os,
            'cpu': asset.cpu,
            'memory': asset.memory,
            'disk': asset.disk,
            'sn': asset.sn,
            'type': asset.type,
            'manufacturer': asset.manufacturer,
            'model': asset.model,
            'asset_number': asset.asset_number,
            'cabinet_number': asset.cabinet_number,
            'cabinet_position': asset.cabinet_position,
            'is_online': asset.is_online,
            'status': asset.status,
            'manager': asset.manager,
            'applications': asset.applications,
            'asset_groups': group_name,
            'idc': asset.idc.name
        })

@api.route('/api/assets/<int:asset_id>',methods = ['DELETE'])
@auth.login_required
def delete_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if asset is None:
        abort(404)
    db.session.delete(asset)
    return jsonify({'result': True})





