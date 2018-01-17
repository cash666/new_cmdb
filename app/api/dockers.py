# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 14:38
# @Author  : caoshuai
# @File    : dockers.py
# @Software: PyCharm

from flask import jsonify,abort,make_response,request,url_for,current_app
from authentication import auth
from . import api
from app import db
from app.docker.models import DockerImage,DockerContainer
import datetime

@api.route('/api/images',methods = ['GET'])
@auth.login_required
def get_images():
    page = request.args.get('page', 1, type=int)
    pagination = DockerImage.query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    images = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_images', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_images', page=page + 1, _external=True)
    image_list = []
    for image in images:
        image_list.append({
            'url': url_for('api.get_image', image_id = image.id, _external=True),
            'image_name':image.image_name,
            'tag_name':image.tag_name,
            'image_id':image.image_id,
            'creater':image.creater,
            'dockerfile':image.dockerfile.name,
            'create_time':datetime.datetime.strftime(image.create_time, '%Y-%m-%d %H:%M:%S') if image.create_time else '-',
            'prev':prev,
            'next':next,
            'count':pagination.total,
        })
    return jsonify(image_list)

@api.route('/api/images/<int:image_id>',methods = ['GET'])
@auth.login_required
def get_image(image_id):
    image = DockerImage.query.get(image_id)
    if image is None:
        abort(404)
    return jsonify({
        'url':url_for('api.get_image', image_id = image.id, _external=True),
        'image_name':image.image_name,
        'tag_name':image.tag_name,
        'image_id':image.image_name,
        'creater':image.creater,
        'dockerfile':image.dockerfile.name,
        'create_time':datetime.datetime.strftime(image.create_time, '%Y-%m-%d %H:%M:%S') if image.create_time else '-',
    })

@api.route('/api/containers',methods = ['GET'])
@auth.login_required
def get_containers():
    page = request.args.get('page', 1, type=int)
    pagination = DockerContainer.query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    containers = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_containers', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_containers', page=page + 1, _external=True)
    container_list = []
    for container in containers:
        container_list.append({
            'url': url_for('api.get_container', container_id = container.id, _external=True),
            'container_name':container.container_name,
            'container_id':container.container_id,
            'status':container.status,
            'src_port':container.src_port,
            'dst_port':container.dst_port,
            'image':container.image.image_name,
            'creater':container.creater,
            'create_time':datetime.datetime.strftime(container.create_time, '%Y-%m-%d %H:%M:%S') if container.create_time else '-',
            'prev':prev,
            'next':next,
            'count':pagination.total,
        })
    return jsonify(container_list)

@api.route('/api/containers/<int:container_id>',methods = ['GET'])
@auth.login_required
def get_container(container_id):
    container = DockerContainer.query.get(container_id)
    if container is None:
        abort(404)
    return jsonify({
        'url': url_for('api.get_container', container_id = container.id, _external=True),
        'container_name': container.container_name,
        'container_id': container.container_id,
        'status': container.status,
        'src_port': container.src_port,
        'dst_port': container.dst_port,
        'image': container.image.image_name,
        'creater': container.creater,
        'create_time': datetime.datetime.strftime(container.create_time,'%Y-%m-%d %H:%M:%S') if container.create_time else '-',
    })







