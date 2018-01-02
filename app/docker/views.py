# -*- coding: utf-8 -*-
# @Time    : 2018/01/02 11:35
# @Author  : caoshuai
# @File    : views.py
# @Software: PyCharm Community Edition

from flask import render_template,redirect,url_for,request,jsonify,current_app,session,make_response,send_file,send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename
from . import docker
from .models import DockerFile,DockerImage,DockerContainer
from sqlalchemy import not_,or_
from app import db
from app.utils import mail
import json
import tablib
import os,time
import xlrd

@docker.route('/dockerfile/list/',methods = ['GET','POST'])
@login_required
def dockerfile_list():
    id = request.form.get('id','')
    name = request.form.get('name','')
    path = request.form.get('path','')
    des = request.form.get('des','')
    content = request.form.get('content','')
    search = request.form.get('search','')
    if name and path and content:
        name_exists = DockerFile.query.filter_by(name=name).first()
        path_exists = DockerFile.query.filter_by(path=path).first()
        if name_exists and path_exists:
            return jsonify({
                'result':-1,
                'errMsg':u'Dockerfile名称和Dockerfile路径都已经存在！'
            })
        elif name_exists and not path_exists:
            return jsonify({
                'result': -1,
                'errMsg': u'Dockerfile名称已经存在！'
            })
        elif path_exists and not name_exists:
            return jsonify({
                'result': -1,
                'errMsg': u'Dockerfile路径已经存在！'
            })
        df = DockerFile()
        df.name = name
        df.path = path
        df.content = content
        df.description = des
        df.creater = session.get('username')
        db.session.add(df)
        full_path = os.path.join(current_app.config['DOCKERFILE_PATH'],path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        f = open(os.path.join(full_path,'Dockerfile'),'w')
        f.write(content)
        f.close()
        return jsonify({
            'result':1
        })
    if id and path:
        file = DockerFile.query.get(id)
        if file.content:
            return jsonify({
                'result':1,
                'content':file.content
            })
        elif os.path.exists(os.path.join(current_app.config['DOCKERFILE_PATH'],os.path.join(file.path,'Dockerfile'))):
            f = open(os.path.join(current_app.config['DOCKERFILE_PATH'],os.path.join(file.path,'Dockerfile')),'r')
            content = f.read()
            f.close()
            return jsonify({
                'result': 1,
                'content': content
            })
        else:
            return jsonify({
                'result': -1,
                'errMsg': u'Dockerfile内容为空或不存在！'
            })
    page = request.args.get('page', 1, type=int)
    pagination = DockerFile.query.filter(or_(DockerFile.name.like('%'+search+'%'),DockerFile.path.like('%'+search+'%'),DockerFile.description.like('%'+search+'%'),DockerFile.creater.like('%'+search+'%'))).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    dockerfiles = pagination.items
    return render_template('docker/dockerfile_list.html',dockerfiles = dockerfiles,menu = 'dockerfile_list')



