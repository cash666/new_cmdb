# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 9:57
# @Author  : caoshuai
# @File    : views.py
# @Software: PyCharm Community Edition

from flask import render_template,redirect,url_for,request,jsonify,current_app,session,make_response,send_file,send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename
from . import asset
from .models import Asset,AssetGroup,IDC
from sqlalchemy import not_,or_
from app import db
from app.utils import mail
import json
import tablib
import os,time
import xlrd


@asset.route('/download/',methods = ['GET'])
def show_attachment():
    filename = request.args.get('filename')
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_DIR']),filename,as_attachment=True)

@asset.route('/idc/list/',methods = ['GET','POST'])
@login_required
def idc_list():
    data = request.form.get('data','')
    idc_id = request.form.get('idc_id','')
    type = request.form.get('type','')
    search = request.form.get('search','')
    page = request.args.get('page', 1, type=int)
    pagination = IDC.query.filter(or_(IDC.name.like('%'+search+'%'),IDC.contacts.like('%'+search+'%'),IDC.phone.like('%'+search+'%'),IDC.comment.like('%'+search+'%'))).paginate(page, per_page = current_app.config['PER_PAGE'], error_out=False)
    idcs = pagination.items
    if data and not type:
        json_data = json.loads(data)
        name = json_data.get('name')
        bandwidth = json_data.get('bandwidth')
        contacts = json_data.get('contacts')
        phone = json_data.get('phone')
        address = json_data.get('address')
        network = json_data.get('network')
        operator = json_data.get('operator')
        comment = json_data.get('comment')
        i = IDC()
        i.name = name
        i.bandwidth = bandwidth
        i.contacts = contacts
        i.phone = phone
        i.address = address
        i.network = network
        i.operator = operator
        i.comment = comment
        db.session.add(i)
        return jsonify({
            'result':1
        })
    elif idc_id and type == 'load_idc_info':
        idc = IDC.query.get(idc_id)
        return jsonify({
            "name": idc.name,
            "bandwidth": idc.bandwidth,
            "contacts": idc.contacts,
            "phone": idc.phone,
            "address": idc.address,
            "network": idc.network,
            "operator": idc.operator,
            "comment": idc.comment,
        })
    elif data and type == 'modify_idc_info':
        json_data = json.loads(data)
        i = IDC.query.get(json_data.get('idc_id'))
        name = json_data.get('name')
        bandwidth = json_data.get('bandwidth')
        contacts = json_data.get('contacts')
        phone = json_data.get('phone')
        address = json_data.get('address')
        network = json_data.get('network')
        operator = json_data.get('operator')
        comment = json_data.get('comment')
        i.name = name
        i.bandwidth = bandwidth
        i.contacts = contacts
        i.phone = phone
        i.address = address
        i.network = network
        i.operator = operator
        i.comment = comment
        db.session.merge(i)
        return jsonify({
            'result': 1
        })
    elif idc_id and type == 'delete_idc_info':
        idc = IDC.query.get(idc_id)
        db.session.delete(idc)
        return jsonify({
            'result':1
        })
    elif type == 'load_idc_list':
        idc_list = []
        idcs = IDC.query.all()
        for idc in idcs:
            idc_list.append({
                'id': idc.id,
                'name': idc.name,
            })
        return jsonify(idc_list)
    return render_template('asset/idc_list.html',idcs = idcs,menu = 'idc_list',pagination = pagination)

@asset.route('/asset_group/list/',methods = ['GET','POST'])
@login_required
def asset_group_list():
    search = request.form.get('search', '')
    data = request.form.get('data','')
    group_id = request.form.get('group_id','')
    name = request.form.get('name','')
    comment = request.form.get('comment','')
    type = request.form.get('type','')
    page = request.args.get('page', 1, type=int)
    pagination = AssetGroup.query.filter(or_(AssetGroup.name.like('%'+search+'%'),AssetGroup.comment.like('%'+search+'%'))).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    groups = pagination.items
    if data:
        json_data = json.loads(data)
        assets = json_data.get('assets','')
        group = AssetGroup()
        group.name = json_data.get('name','')
        group.comment = json_data.get('comment','')
        if assets:
            for asset in assets:
                asset_name,asset_innerIP = asset.split('-')
                a = Asset.query.filter_by(hostname = asset_name.strip(),innerIP = asset_innerIP.strip()).first()
                group.assets.append(a)
        db.session.add(group)
        return jsonify({
            'result':1
        })
    elif group_id and not name and not comment:
        group = AssetGroup.query.get(group_id)
        db.session.delete(group)
        return jsonify({
            'result': 1
        })
    elif group_id and name and comment:
        group = AssetGroup.query.get(group_id)
        group.name = name
        group.comment = comment
        db.session.merge(group)
        return jsonify({
            'result': 1
        })
    elif type == 'load_asset_group_list':
        group_list = []
        groups = AssetGroup.query.all()
        for group in groups:
            group_list.append({
                'id': group.id,
                'name': group.name,
            })
        return jsonify(group_list)
    return render_template('asset/asset_group_list.html', groups=groups, menu='asset_group_list',pagination = pagination)

@asset.route('/asset/list/',methods = ['GET','POST'])
@login_required
def asset_list():
    asset_id = request.form.get('asset_id','')
    type = request.form.get('type','')
    data = request.form.get('data','')
    keyword = request.args.get('keyword','')
    file = request.files.get('upload_file')
    status = request.args.get('status','')
    is_online = request.args.get('is_online','')
    group = request.args.get('group','')
    idc = request.args.get('idc','')
    page = request.args.get('page', 1, type=int)
    is_online2 = ''
    idc_list = []
    asset_list = []
    if is_online:
        if is_online == u'运行中':
            is_online2 = '1'
        elif is_online == u'已停止':
            is_online2 = '0'
    if idc:
        idcs = IDC.query.filter(IDC.name == idc).first()
        idc_list.append(idcs.id)
    if group:
        groups = AssetGroup.query.filter(AssetGroup.name == group).first()
        for a in groups.assets.all():
            asset_list.append(a.id)
    query = Asset.query
    if keyword:
        query = query.filter(or_(Asset.hostname.like('%' + keyword + '%'),Asset.innerIP.like('%' + keyword + '%'), Asset.outerIP.like('%' + keyword + '%'),Asset.os.like('%' + keyword + '%')))
    if idc:
        query = query.filter(Asset.idc_id.in_(idc_list))
    if group:
        query = query.filter(Asset.id.in_(asset_list))
    if status:
        query = query.filter(Asset.status == status)
    if is_online:
        query = query.filter(Asset.is_online == is_online2)
    pagination = query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    assets = pagination.items
    if data and not type:
        json_data = json.loads(data)
        a = Asset()
        a.hostname = json_data.get('hostname','')
        a.innerIP = json_data.get('innerIP','')
        a.outerIP = json_data.get('outerIP','')
        a.os = json_data.get('os','')
        a.cpu = json_data.get('cpu','')
        a.memory = json_data.get('memory','')
        a.disk = json_data.get('disk','')
        a.sn = json_data.get('sn','')
        a.type = json_data.get('type','')
        a.manufacturer = json_data.get('manufacturer','')
        a.model = json_data.get('model','')
        a.asset_number = json_data.get('asset_number','')
        a.cabinet_number = json_data.get('cabinet_number','')
        a.cabinet_position = json_data.get('cabinet_position','')
        a.is_online = True if json_data.get('is_online','0') == '1' else False
        a.status = json_data.get('status','')
        a.manager = json_data.get('manager','')
        a.applications = json_data.get('applications','')
        a.comment = json_data.get('comment','')
        a.idc_id = json_data.get('idc')
        group_list = json_data.get('group')
        for group_id in group_list:
            group = AssetGroup.query.get(group_id)
            a.asset_groups.append(group)
        db.session.add(a)
        return jsonify({
            'result':1
        })
    elif asset_id and type == 'load_asset_info':
        asset = Asset.query.get(asset_id)
        group_list = []
        for group in asset.asset_groups.all():
            group_list.append(group.name)
        return jsonify({
            "hostname": asset.hostname,
            "innerIP": asset.innerIP,
            "outerIP": asset.outerIP,
            "os": asset.os,
            "cpu": asset.cpu,
            "memory": asset.memory,
            "disk": asset.disk,
            "sn": asset.sn,
            "type": asset.type,
            "manufacturer": asset.manufacturer,
            "model": asset.model,
            "asset_number": asset.asset_number,
            "cabinet_number": asset.cabinet_number,
            "cabinet_position": asset.cabinet_position,
            "status": asset.status,
            "is_online": asset.is_online,
            "manager": asset.manager,
            "applications": asset.applications,
            "comment": asset.comment,
            "group": group_list,
            "idc": asset.idc_id,
        })
    elif data and type == 'modify':
        json_data = json.loads(data)
        a = Asset.query.get(json_data.get('asset_id'))
        a.hostname = json_data.get('hostname', '')
        a.innerIP = json_data.get('innerIP', '')
        a.outerIP = json_data.get('outerIP', '')
        a.os = json_data.get('os', '')
        a.cpu = json_data.get('cpu', '')
        a.memory = json_data.get('memory', '')
        a.disk = json_data.get('disk', '')
        a.sn = json_data.get('sn', '')
        a.type = json_data.get('type', '')
        a.manufacturer = json_data.get('manufacturer', '')
        a.model = json_data.get('model', '')
        a.asset_number = json_data.get('asset_number', '')
        a.cabinet_number = json_data.get('cabinet_number', '')
        a.cabinet_position = json_data.get('cabinet_position', '')
        a.is_online = True if json_data.get('is_online', '0') == '1' else False
        a.status = json_data.get('status', '')
        a.manager = json_data.get('manager', '')
        a.applications = json_data.get('applications', '')
        a.comment = json_data.get('comment', '')
        a.idc_id = json_data.get('idc')
        group_list = json_data.get('group')
        for group in a.asset_groups.all():
            a.asset_groups.remove(group)
        for group_name in group_list:
            group = AssetGroup.query.filter_by(name = group_name).first()
            a.asset_groups.append(group)
        db.session.merge(a)
        return jsonify({
            'result': 1
        })
    elif asset_id and type == 'delete':
        asset = Asset.query.get(asset_id)
        for group in asset.asset_groups.all():
            asset.asset_groups.remove(group)
        db.session.delete(asset)
        return jsonify({
            'result': 1
        })
    elif file:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            asset_template = os.path.join(os.getcwd(), "%s\\%s" % (current_app.config['UPLOAD_DIR'], filename))
            file.save(asset_template)
            data = xlrd.open_workbook(asset_template)
            table = data.sheets()[0]
            rows = table.nrows
            count = 0
            if int(rows) > 1:
                for i in range(1,int(rows)):
                    asset_info = table.row_values(i)
                    a = Asset()
                    a.hostname = asset_info[0].strip()
                    a.innerIP = asset_info[1].strip()
                    a.outerIP = asset_info[2].strip()
                    a.os = asset_info[3].strip()
                    a.cpu = asset_info[4].strip()
                    a.memory = asset_info[5].strip()
                    a.disk = asset_info[6].strip()
                    a.sn = asset_info[7].strip()
                    a.type = asset_info[8].strip()
                    a.manufacturer = asset_info[9].strip()
                    a.model = asset_info[10].strip()
                    a.asset_number = asset_info[11].strip()
                    a.cabinet_number = asset_info[12].strip()
                    a.cabinet_position = asset_info[13].strip()
                    a.is_online = True if asset_info[14] == '1' else False
                    a.status = asset_info[15].strip()
                    a.manager = asset_info[16].strip()
                    a.applications = asset_info[17].strip()
                    idc = IDC.query.filter_by(name = asset_info[19].strip()).first()
                    if idc is not None:
                        idc_id = idc.id
                    else:
                        idc_id = 1
                    a.idc_id = idc_id
                    group_name = asset_info[18].strip()
                    if group_name.find(','):
                        group_list = group_name.split(',')
                    else:
                        group_list = [group_name]
                    for group in group_list:
                        g = AssetGroup.query.filter_by(name = group).first()
                        if g is not None:
                            count = count + 1
                            a.asset_groups.append(g)
                    if count == 0:
                        g = AssetGroup.query.filter_by(name='yunwei').first()
                        a.asset_groups.append(g)
                    db.session.add(a)
                    os.remove(asset_template)
                    return jsonify({
                        'result':1
                    })
    elif type == 'load_asset_list':
        assets = Asset.query.all()
        asset_list = []
        for asset in assets:
            asset_list.append({
                'asset_name': asset.hostname+' - '+asset.innerIP
            })
        return jsonify(asset_list)
    return render_template('asset/asset_list.html', assets = assets, menu = 'asset_list',pagination = pagination, status = status,is_online = is_online,status_list = current_app.config['STATUS_LIST'],online_list = current_app.config['ONLINE_LIST'],idc = idc,group = group,keyword = keyword)

@asset.route('/asset/export/',methods = ['GET','POST'])
@login_required
def export_asset():
    headers = (u'主机名',u'内网IP',u'外网IP',u'操作系统','CPU',u'内存',u'硬盘',u'序列号',u'主机类型',u'厂商',u'型号',u'资产编号',u'机柜号',u'机柜位置',u'运行状态',u'状态',u'负责人',u'应用',u'资产组',u'所属IDC')
    assets = Asset.query.all()
    asset_info = []
    for asset in assets:
        group_name = ''
        for group in asset.asset_groups.all():
            if group_name:
                group_name = '%s,%s' % (group_name,group.name)
            else:
                group_name = group.name
        if asset.is_online:
            is_online = u'运行中'
        else:
            is_online = u'已停止'
        asset_info.append([asset.hostname,asset.innerIP,asset.outerIP,asset.os,asset.cpu,asset.memory,asset.disk,asset.sn,asset.type,asset.manufacturer,asset.model,asset.asset_number,asset.cabinet_number,asset.cabinet_position,is_online,asset.status,asset.manager,asset.applications,group_name,asset.idc.name])
    data = tablib.Dataset(*asset_info, headers=headers)
    download_filename = 'upload\\asset_%s.xls' % int(time.time())
    f = file(download_filename, 'wb')
    f.write(data.xls)
    f.close()
    download_file = os.path.join(os.getcwd(),download_filename)
    response = make_response(send_file(download_file))
    response.headers["Content-Disposition"] = "attachment; filename=%s;" % os.path.basename(download_filename)
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ['xls','xlsx']