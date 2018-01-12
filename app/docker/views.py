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
import docker as new_docker

class DockerClient(object):

    @staticmethod
    def client():
        client = new_docker.DockerClient(base_url='unix://var/run/docker.sock')
        return client

@docker.route('/dockerfile/list/',methods = ['GET','POST'])
@login_required
def dockerfile_list():
    id = request.form.get('id','')
    image_name = request.form.get('image_name','')
    name = request.form.get('name','')
    path = request.form.get('path','')
    des = request.form.get('des','')
    content = request.form.get('content','')
    file = request.files.get('file','')
    search = request.form.get('search','')
    type = request.form.get('type','')
    if type == 'load_dockerfile_list':
        dockerfile_list = []
        docker_files = DockerFile.query.all()
        for f in docker_files:
            dockerfile_list.append({
                'id': f.id,
                'name': f.name,
            })
        return jsonify(dockerfile_list)
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
        full_path = os.path.join(current_app.config['DOCKERFILE_PATH'], path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        f = open(os.path.join(full_path, 'Dockerfile'), 'w')
        f.write(content)
        f.close()
        df = DockerFile()
        df.name = name
        df.path = path
        df.content = content
        if file:
            filename = secure_filename(file.filename)
            dockerfile_attachment = os.path.join(full_path,filename)
            file.save(dockerfile_attachment)
        else:
            filename = ''
        df.attachment = filename
        df.description = des
        df.creater = session.get('username')
        db.session.add(df)
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
    elif id and image_name:
        df = DockerFile.query.get(id)
        docker_file_path = os.path.join(current_app.config['DOCKERFILE_PATH'],df.path)
        if os.path.exists(docker_file_path):
            c = DockerClient.client()
            try:
                c.images.get(image_name)
            except Exception,e:
                pass
            else:
                return jsonify({
                    "result":-1,
                    "errMsg":u'镜像已经存在！',
                })
            try:
                c.images.build(tag = image_name,path = docker_file_path)
            except Exception,e:
                return jsonify({
                    "result":1,
                    "errMsg":u'镜像创建失败，报错：%s！' % e,
                })
            else:
                dm = DockerImage()
                dm.image_name = image_name
                dm.tag_name = "latest"
                image = c.images.get(image_name)
                image_id = image.id
                dm.image_id = image_id.split(':')[1]
                dm.creater = session.get('username')
                dm.dockerfile_id = id
                db.session.add(dm)
                #推到私有仓库
                try:
                    os.system("docker tag %s %s/%s" % (image_name,current_app.config['DOCKER_REGISTRY'],image_name))
                    c.images.push("%s/%s" % (current_app.config['DOCKER_REGISTRY'],image_name),insecure_registry = True)
                except Exception,e:
                    pass
                return jsonify({
                    "result":1,
                })
        else:
            return jsonify({
                'result':-1,
                'errMsg':u'镜像不能创建，因为Dockerfile不存在！',
            })
    page = request.args.get('page', 1, type=int)
    pagination = DockerFile.query.filter(or_(DockerFile.name.like('%'+search+'%'),DockerFile.path.like('%'+search+'%'),DockerFile.description.like('%'+search+'%'),DockerFile.creater.like('%'+search+'%'))).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    dockerfiles = pagination.items
    return render_template('docker/dockerfile_list.html',dockerfiles = dockerfiles,menu = 'dockerfile_list')


@docker.route('/docker/image/list/',methods = ['GET','POST'])
@login_required
def dockerimage_list():
    id = request.form.get('id','')
    search = request.form.get('search', '')
    page = request.args.get('page', 1, type=int)
    pagination = DockerImage.query.filter(or_(DockerImage.image_name.like("%"+search+"%"),DockerImage.image_id.like("%"+search+"%"),DockerImage.creater.like("%"+search+"%"))).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    dockerimages = pagination.items
    type = request.form.get('type','')
    data = request.form.get('data', '')
    if type == 'load_image_list':
        image_list = []
        images = DockerImage.query.all()
        for image in images:
            image_list.append({
                'id':image.id,
                'image_name':image.image_name,
            })
        return jsonify(image_list)
    elif id:
        image = DockerImage.query.get(id)
        image_name = image.image_name
        db.session.delete(image)
        c = DockerClient.client()
        try:
            c.images.remove(image = "%s/%s" % (current_app.config['DOCKER_REGISTRY'],image_name))
        except Exception,e:
            return jsonify({
                "result":-1,
                "errMsg":str(e)
            })
        else:
            return jsonify({
                'result':1
            })
    elif data:
        json_data = json.loads(data)
        image_name = json_data.get('image_name','')
        image_tag = json_data.get('image_tag','')
        image_id = json_data.get('image_id','')
        docker_file = json_data.get('docker_file','')
        image = DockerImage()
        image.image_name = image_name
        image.tag_name = image_tag if image_tag else 'latest'
        image.image_id = image_id
        image.creater = session.get('username')
        image.dockerfile_id = docker_file
        db.session.add(image)
        return jsonify({
            'result':1
        })
    return render_template('docker/dockerimage_list.html', dockerimages=dockerimages, menu='dockerimage_list',pagination=pagination)

@docker.route('/docker/container/list/',methods = ['GET','POST'])
@login_required
def dockercontainer_list():
    page = request.args.get('page', 1, type=int)
    query = DockerContainer.query
    type = request.form.get('type', '')
    data = request.form.get('data','')
    container_id = request.form.get('container_id','')
    image_name = request.form.get('image_name','')
    message = request.form.get('message','')
    force = request.form.get('force','')
    keyword = request.args.get('keyword', '')
    is_online = request.args.get('is_online', '')
    is_delete_volume = request.form.get('is_delete_volume','')
    is_delete_link = request.form.get('is_delete_link','')
    tag = request.form.get('tag', '')
    if is_online:
        if is_online == u'运行中':
            is_online2 = '1'
        elif is_online == u'已停止':
            is_online2 = '0'
    if keyword:
        query = query.filter(or_(DockerContainer.container_name.like('%' + keyword + '%'),DockerContainer.container_id.like('%' + keyword + '%'), DockerContainer.src_port.like('%' + keyword + '%'),DockerContainer.dst_port.like('%' + keyword + '%'),DockerContainer.creater.like('%' + keyword + '%')))
    if is_online:
        query = query.filter(DockerContainer.status == is_online2)
    pagination = query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    dockercontainers = pagination.items
    if container_id and force:
        c = DockerClient.client()
        container = c.containers.get(container_id)
        try:
            if force == '0':
                container.stop(5)
            elif force == '1':
                container.kill()
        except Exception,e:
            return jsonify({
                'result': -1,
                'errMsg': str(e)
            })
        else:
            return jsonify({
                'result': 1
            })
    if container_id and image_name and message:
        if not tag:
            tag = 'latest'
        try:
            c = DockerClient.client()
            container = c.containers.get(container_id)
            container.commit(image_name,tag = tag,author = session.get('username'),message = message)
            os.system("docker tag %s:%s %s/%s:%s" % (image_name,tag,current_app.config['DOCKER_REGISTRY'], image_name,tag))
            c.images.push("%s/%s:%s" % (current_app.config['DOCKER_REGISTRY'], image_name,tag), insecure_registry=True)
        except Exception,e:
            return jsonify({
                'result':-1,
                'errMsg':str(e)
            })
        else:
            image = DockerImage()
            image.image_name = image_name
            image.tag_name = tag
            res = c.images.get("%s:%s" % (image_name, tag))
            image.image_id = res.id.split(':')[1]
            image.creater = session.get('username')
            dc = DockerContainer.query.filter_by(container_id=container_id).first()
            di = DockerImage.query.get(dc.image_id)
            image.dockerfile_id = di.dockerfile_id
            db.session.add(image)
            return jsonify({
                'result':1
            })
    if data:
        json_data = json.loads(data)
        container_name = json_data.get('container_name','')
        image_name = json_data.get('image_name','')
        src_port = json_data.get('src_port','')
        dst_port = json_data.get('dst_port','')
        host_dir = json_data.get('host_dir','')
        container_dir = json_data.get('container_dir','')
        model = json_data.get('model','')
        container_name2 = json_data.get('container_name2','')
        command = json_data.get('command','')
        status = json_data.get('status','')
        image = DockerImage.query.get(image_name)
        try:
            c = DockerClient.client()
            if dst_port:
                if not src_port:
                    port_dict = {'%s/tcp' % int(dst_port): None}
                elif src_port.find(',')>=0:
                    src_port_list = src_port.split(',')
                    new_src_port_list = []
                    for p in src_port_list:
                        if p != '':
                            new_src_port_list.append(int(p))
                    port_dict = {'%s/tcp' % int(dst_port): new_src_port_list}
                else:
                    port_dict = {'%s/tcp' % int(dst_port): int(src_port)}
            else:
                port_dict = {}
            if host_dir and container_dir:
                if model:
                    volume_dict = {'%s' % host_dir: {'bind': '%s' % container_dir, 'mode': '%s' % model}}
                else:
                    volume_dict = {'%s' % host_dir: {'bind': '%s' % container_dir, 'mode': 'ro'}}
            else:
                volume_dict = {}
            if container_name2:
                volumes_from = [container_name2]
            else:
                volumes_from = []
            if status:
                if status == '0':
                    detach = False
                else:
                    detach = True
            c.containers.run(image = image.image_name,name = container_name,ports = port_dict,volumes = volume_dict,volumes_from = volumes_from,command = command,detach = detach,tty = True)
        except Exception,e:
            return jsonify({
                'result':-1,
                'errMsg':str(e),
            })
        else:
            dc = DockerContainer()
            dc.container_name = container_name
            container = c.containers.get(container_name)
            dc.container_id = container.short_id
            dc.status = detach
            dc.src_port = src_port
            dc.dst_port = dst_port
            dc.image_id = image_name
            dc.creater = session.get('username')
            db.session.add(dc)
            return jsonify({'result':1})
    if type == 'load_container_list':
        container_list = []
        containers = DockerContainer.query.all()
        for container in containers:
            container_list.append({
                'id': container.id,
                'container_name': container.container_name,
            })
        return jsonify(container_list)
    if type == 'start_container':
        c = DockerClient.client()
        container = c.containers.get(container_id)
        try:
            container.start()
        except Exception,e:
            return jsonify({
                'result': -1,
                'errMsg': str(e),
            })
        else:
            dc = DockerContainer.query.filter_by(container_id = container_id).first()
            dc.status = 1
            db.session.merge(dc)
            return jsonify({'result': 1})
    if type == 'restart_container':
        c = DockerClient.client()
        container = c.containers.get(container_id)
        try:
            container.restart(5)
        except Exception,e:
            return jsonify({
                'result': -1,
                'errMsg': str(e),
            })
        else:
            return jsonify({'result': 1})

    if container_id and is_delete_volume and is_delete_link:
        c = DockerClient.client()
        container = c.containers.get(container_id)
        if is_delete_volume == '0':
            volume = False
        else:
            volume = True
        if is_delete_link == '0':
            link = False
        else:
            link = True
        try:
            container.remove(v = volume,link = link,force = True)
        except Exception,e:
            return jsonify({
                'result': -1,
                'errMsg': str(e),
            })
        else:
            dc = DockerContainer.query.filter_by(container_id = container_id).first()
            db.session.delete(dc)
            return jsonify({'result': 1})
    if container_id and type == 'show_container_info':
        c = DockerClient.client()
        container = c.containers.get(container_id)
        try:
            logs = container.logs(timestamps = True)
            processes = container.top(ps_args = 'aux')
        except Exception,e:
            return jsonify({
                'result':-1,
                'errMsg':str(e)
            })
        else:
            info_dict = {}
            log_list = logs.split('\n')
            info_dict['log'] = log_list
            info_dict['process'] = processes
            return jsonify(info_dict)
    return render_template('docker/dockercontainer_list.html', dockercontainers=dockercontainers, menu='dockercontainer_list',pagination=pagination,online_list = current_app.config['ONLINE_LIST'],is_online = is_online,keyword = keyword)
