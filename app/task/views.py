# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 16:39
# @Author  : caoshuai
# @File    : views.py
# @Software: PyCharm Community Edition

from flask import render_template,request,jsonify,session,send_from_directory,current_app
from . import task
from flask_login import login_required
from .models import Task,Project,TaskFlow,TaskTemplate
from app.auth.models import User
import json,os,base64,time
from app import db
import datetime
from app import app
from app.utils import mail
from sqlalchemy import or_

@task.route('/download/',methods = ['GET'])
def show_attachment():
    filename = request.args.get('filename')
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_DIR']),filename,as_attachment=True)

@task.route('/task/apply/',methods = ['GET','POST'])
@login_required
def task_apply():
    data = request.form.get('data','')
    type = request.form.get('type','')
    template_id = request.form.get('template_id','')
    if data and type == 'template':
        data = json.loads(data)
        is_exists = TaskTemplate.query.filter_by(template_name=data.get('project_name')).first()
        if is_exists:
            return jsonify({
                'result':-1,
                'errMsg':u'模板名已经存在，可以改下项目名！'
            })
        else:
            t = TaskTemplate()
            t.template_name = data.get('project_name','')
            t.template_owner = data.get('applicant','')
            t.project_name = data.get('project_name','')
            t.project_domain = data.get('project_domain','')
            t.applicant = data.get('applicant','')
            t.manager = data.get('manager','')
            t.online_time = data.get('online_time','')
            t.is_test = True if data.get('is_test','0') == '1' else False
            t.emergent = data.get('emergent','')
            t.git_url = data.get('git_url','')
            t.start_command = data.get('start_command','')
            t.start_port = data.get('start_port','')
            t.is_public = True if data.get('is_public','0') == '1' else False
            t.is_nginx = True if data.get('is_nginx','0') == '1' else False
            t.is_crossdomain = True if data.get('is_crossdomain','0') == '1' else False
            t.is_mysql = True if data.get('is_mysql','0') == '1' else False
            t.is_postgresql = True if data.get('is_postgresql','0') == '1' else False
            t.is_redis = True if data.get('is_redis','0') == '1' else False
            t.redis_prefix = data.get('redis_prefix','')
            t.is_memcache = True if data.get('is_memcache','0') == '1' else False
            t.memcache_prefix = data.get('memcache_prefix','')
            t.is_ssdb = True if data.get('is_ssdb','0') == '1' else False
            t.ssdb_prefix = data.get('ssdb_prefix','')
            t.is_kafka = True if data.get('is_kafka','0') == '1' else False
            t.kafka_prefix = data.get('kafka_prefix','')
            t.is_rabbitMQ = True if data.get('is_rabbitMQ','0') == '1' else False
            t.host_type = data.get('host_type','')
            t.host_configuration = data.get('host_configuration','')
            t.check_status = u'待审核'
            t.publisher = data.get('publisher','')
            t.checker = data.get('checker','')
            t.is_daemon = True if data.get('is_daemon','0') == '1' else False
            t.daemon_mode = data.get('daemon_mode','')
            t.is_test_url = True if data.get('is_test_url','0') == '1' else False
            t.test_url = data.get('test_url','')
            t.is_slb = True if data.get('is_slb','0') == '1' else False
            t.ha_special = data.get('ha_special','')
            t.service_type = data.get('service_type','')
            t.is_log = True if data.get('is_log','0') == '1' else False
            t.log_position = data.get('log_position','')
            t.log_special_position = data.get('log_special_position','')
            t.is_log_cut = True if data.get('is_log_cut','0') == '1' else False
            t.log_clear = data.get('log_clear','')
            t.is_log_cut_by_operation = True if data.get('is_log_cut_by_operation','0') == '1' else False
            t.comment = data.get('comment','')
            file = data.get('file','')
            attachment_list = data.get('attachment','')
            if attachment_list and file:
                if not os.path.exists(app.config['UPLOAD_DIR']):
                    os.makedirs(app.config['UPLOAD_DIR'])
                attachment = attachment_list[0]
                start = attachment.find(',')
                attachment_data = attachment[start + 1:]
                attachment_content = base64.b64decode(attachment_data)
                unix_time = int(time.time())
                ext = os.path.splitext(file)[1]
                new_filename = os.path.join(app.config['UPLOAD_DIR'],str(unix_time) + ext)
                f = open(new_filename,'w')
                f.write(attachment_content)
                f.close()
                t.attachment = new_filename
            db.session.add(t)
            return jsonify({
                'result':1
            })
    elif type == 'create_task':
        data = json.loads(data)
        is_exists = Task.query.filter_by(project_name=data.get('project_name')).first()
        print data
        if is_exists:
            return jsonify({
                'result': -1,
                'errMsg': u'项目名已经存在，请修改！'
            })
        else:
            t = Task()
            t.project_name = data.get('project_name', '')
            t.project_domain = data.get('project_domain', '')
            t.applicant = data.get('applicant', '')
            t.manager = data.get('manager', '')
            t.online_time = data.get('online_time', '')
            t.is_test = True if int(data.get('is_test')) == 1 else False
            t.emergent = data.get('emergent', '')
            t.git_url = data.get('git_url', '')
            t.start_command = data.get('start_command', '')
            t.start_port = data.get('start_port', '')
            t.is_public = True if int(data.get('is_public')) == 1 else False
            t.is_nginx = True if int(data.get('is_nginx')) == 1 else False
            t.is_crossdomain = True if int(data.get('is_crossdomain')) == 1 else False
            t.is_mysql = True if int(data.get('is_mysql')) == 1 else False
            t.is_postgresql = True if int(data.get('is_postgresql')) == 1 else False
            t.is_redis = True if int(data.get('is_redis')) == 1 else False
            t.redis_prefix = data.get('redis_prefix', '')
            t.is_memcache = True if int(data.get('is_memcache')) == 1 else False
            t.memcache_prefix = data.get('memcache_prefix', '')
            t.is_ssdb = True if int(data.get('is_ssdb')) == 1 else False
            t.ssdb_prefix = data.get('ssdb_prefix', '')
            t.is_kafka = True if int(data.get('is_kafka')) == 1 else False
            t.kafka_prefix = data.get('kafka_prefix', '')
            t.is_rabbitMQ = True if int(data.get('is_rabbitMQ')) == 1 else False
            t.host_type = data.get('host_type', '')
            t.host_configuration = data.get('host_configuration', '')
            t.check_status = u'待审核'
            t.publisher = data.get('publisher', '')
            t.checker = data.get('checker', '')
            t.is_daemon = True if int(data.get('is_daemon')) == 1 else False
            t.daemon_mode = data.get('daemon_mode', '')
            t.is_test_url = True if int(data.get('is_test_url')) == 1 else False
            t.test_url = data.get('test_url', '')
            t.is_slb = True if int(data.get('is_slb')) == 1 else False
            t.ha_special = data.get('ha_special', '')
            t.service_type = data.get('service_type', '')
            t.is_log = True if int(data.get('is_log')) == 1 else False
            t.log_position = data.get('log_position', '')
            t.log_special_position = data.get('log_special_position', '')
            t.is_log_cut = True if int(data.get('is_log_cut')) == 1 else False
            t.log_clear = data.get('log_clear', '')
            t.is_log_cut_by_operation = True if int(data.get('is_log_cut_by_operation')) == 1 else False
            t.comment = data.get('comment', '')
            file = data.get('file', '')
            attachment_list = data.get('attachment', '')
            if attachment_list and file:
                if not os.path.exists(app.config['UPLOAD_DIR']):
                    os.makedirs(app.config['UPLOAD_DIR'])
                attachment = attachment_list[0]
                start = attachment.find(',')
                attachment_data = attachment[start + 1:]
                attachment_content = base64.b64decode(attachment_data)
                unix_time = int(time.time())
                ext = os.path.splitext(file)[1]
                new_filename = os.path.join(app.config['UPLOAD_DIR'], str(unix_time) + ext)
                f = open(new_filename, 'w')
                f.write(attachment_content)
                f.close()
                t.attachment = new_filename
            db.session.add(t)
            f = TaskFlow()
            f.task_name = data.get('project_name', '')
            f.operator = data.get('publisher', '')
            f.applicant = data.get('applicant', '')
            f.task_status = u'待审核'
            f.comment = data.get('comment','')
            t = Task.query.filter_by(project_name = data.get('project_name', '')).first()
            f.task_id = t.id
            db.session.add(f)
            return jsonify({
                'result': 1
            })
    elif type == 'load_template':
        template_list = []
        templates = TaskTemplate.query.filter_by(template_owner = session.get('username'))
        if templates:
            for template in templates:
                template_list.append({
                    'template_id':template.id,
                    'template_name':template.template_name,
                })
        return jsonify(template_list)
    elif template_id:
        template = TaskTemplate.query.get(template_id)
        if template.attachment:
            attachment = os.path.basename(template.attachment)
        return jsonify({
            "project_name":template.project_name,
            "git_url": template.git_url,
            "host_type": template.host_type,
            "applicant": template.applicant,
            "manager": template.manager,
            "publisher": template.publisher,
            "checker": template.checker,
            "project_domain": template.project_domain,
            "online_time": template.online_time,
            "is_test": template.is_test,
            "mergent": template.emergent,
            "start_command": template.start_command,
            "start_port": template.start_port,
            "is_public": template.is_public,
            "is_nginx": template.is_nginx,
            "is_crossdomain": template.is_crossdomain,
            "is_mysql": template.is_mysql,
            "is_postgresql": template.is_postgresql,
            "is_redis": template.is_redis,
            "redis_prefix": template.redis_prefix,
            "is_memcache": template.is_memcache,
            "memcache_prefix": template.memcache_prefix,
            "is_ssdb": template.is_ssdb,
            "ssdb_prefix": template.ssdb_prefix,
            "is_kafka": template.is_kafka,
            "kafka_prefix": template.kafka_prefix,
            "is_rabbitMQ": template.is_rabbitMQ,
            "host_configuration": template.host_configuration,
            "is_daemon": template.is_daemon,
            "daemon_mode": template.daemon_mode,
            "is_test_url": template.is_test_url,
            "test_url": template.test_url,
            "is_slb": template.is_slb,
            "ha_special": template.ha_special,
            "service_type": template.service_type,
            "is_log": template.is_log,
            "log_position": template.log_position,
            "is_log_cut": template.is_log_cut,
            "log_clear": template.log_clear,
            "attachment":attachment if template.attachment else '',
        })
    return render_template('task/apply_task.html',menu = 'create_task')

@task.route('/task/check/',methods = ['GET','POST'])
@login_required
def task_check():
    task_id = request.form.get('task_id','')
    status = request.form.get('status','')
    applicant = request.form.get('applicant','')
    reject_reason = request.form.get('reject_reason','')
    publisher = request.form.get('publisher','')
    page = request.args.get('page', 1, type=int)
    if session.get('role') == 'admin':
        pagination = Task.query.filter_by(check_status=u'待审核').paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    else:
        pagination = Task.query.filter_by(check_status = u'待审核',checker = session.get('username')).paginate(page, per_page=current_app.config['PER_PAGE'],error_out=False)
    check_tasks = pagination.items
    if task_id and status and applicant:
        task = Task.query.get(task_id)
        tf = TaskFlow()
        tf.task_name = task.project_name
        tf.operator = session.get('username','')
        tf.applicant = applicant
        tf.task_id = task_id
        if status == '1':
            task.check_status = u'通过'
            tf.task_status = u'通过'
        elif status == '0' and reject_reason:
            task.check_status = u'拒绝'
            task.comment = reject_reason
            tf.task_status = u'拒绝'
            tf.comment = reject_reason
        db.session.merge(task)
        db.session.add(tf)
        u = User.query.filter_by(name = applicant).first()
        email = u.email
        mail.send_mail(u'项目上线审核状态通知', ['%s' % email], 'task_check', applicant = applicant,status = status,project_name = task.project_name,reject_reason = reject_reason)
        return jsonify({
            'result':1
        })
    elif task_id and not status and not applicant and not publisher:
        task = Task.query.get(task_id)
        if task.attachment:
            attachment = os.path.basename(task.attachment)
        return jsonify({
            "project_name": task.project_name,
            "git_url": task.git_url,
            "host_type": task.host_type,
            "applicant": task.applicant,
            "manager": task.manager,
            "publisher": task.publisher,
            "checker": task.checker,
            "check_status": task.check_status,
            "project_domain": task.project_domain if task.project_domain else '-',
            "online_time": task.online_time if task.online_time else '-',
            "create_time": datetime.datetime.strftime(task.create_time,'%Y-%m-%d %H:%M:%S') if task.create_time else '-',
            "is_test": task.is_test,
            "emergent": task.emergent if task.emergent else '-',
            "start_command": task.start_command if task.start_command else '-',
            "start_port": task.start_port if task.start_port else '-',
            "is_public": task.is_public,
            "is_nginx": task.is_nginx,
            "is_crossdomain": task.is_crossdomain,
            "is_mysql": task.is_mysql,
            "is_postgresql": task.is_postgresql,
            "is_redis": task.is_redis,
            "redis_prefix": task.redis_prefix if task.redis_prefix else '-',
            "is_memcache": task.is_memcache,
            "memcache_prefix": task.memcache_prefix if task.memcache_prefix else '-',
            "is_ssdb": task.is_ssdb,
            "ssdb_prefix": task.ssdb_prefix if task.ssdb_prefix else '-',
            "is_kafka": task.is_kafka,
            "kafka_prefix": task.kafka_prefix if task.kafka_prefix else '-',
            "is_rabbitMQ": task.is_rabbitMQ,
            "host_configuration": task.host_configuration if task.host_configuration else '-',
            "is_daemon": task.is_daemon,
            "daemon_mode": task.daemon_mode if task.daemon_mode else '-',
            "is_test_url": task.is_test_url,
            "test_url": task.test_url if task.test_url else '-',
            "is_slb": task.is_slb,
            "ha_special": task.ha_special if task.ha_special else '-',
            "service_type": task.service_type if task.service_type else '-',
            "is_log": task.is_log,
            "log_position": task.log_position if task.log_position else '-',
            "is_log_cut": task.is_log_cut,
            "log_clear": task.log_clear if task.log_clear else '-',
            "attachment": attachment if task.attachment else '-',
            "comment": task.comment if task.comment else '-',
        })
    elif task_id and publisher:
        task = Task.query.get(task_id)
        task.publisher = publisher
        db.session.merge(task)
        return jsonify({
            'result':1
        })
    return render_template('task/check_task.html',check_tasks = check_tasks,menu = 'check_task_list',pagination = pagination)

@task.route('/task/list/',methods = ['GET','POST'])
@login_required
def task_list():
    task_id = request.form.get('task_id','')
    type = request.form.get('type','')
    search = request.form.get('search','')
    page = request.args.get('page', 1, type=int)
    pagination = Task.query.filter(Task.check_status==u'完成',or_(Task.project_name.like('%'+search+'%'),Task.checker.like('%'+search+'%'),Task.publisher.like('%'+search+'%'),Task.applicant.like('%'+search+'%'))).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    completed_tasks = pagination.items
    if task_id and not type:
        flows = TaskFlow.query.filter_by(task_id = task_id)
        if flows:
            flow_list = []
            for f in flows:
                flow_list.append({
                    'task_name':f.task_name,
                    'operator':f.operator,
                    'applicant':f.applicant,
                    'task_status':f.task_status,
                    'comment':f.comment,
                    'create_time':datetime.datetime.strftime(f.create_time,'%Y-%m-%d %H:%M:%S'),
                })
            return jsonify(flow_list)
    elif task_id and type == 'info':
        task = Task.query.get(task_id)
        if task.is_mysql or task.is_postgresql:
            db_ip = task.project.db_ip
            db_name = task.project.db_name
        else:
            db_ip = '-'
            db_name = '-'
        if task.is_redis:
            redis_ip = task.project.redis_ip
            redis_port = task.project.redis_port
        else:
            redis_ip = '-'
            redis_port = '-'
        if task.is_memcache:
            memcache_ip = task.project.memcache_ip
            memcache_port = task.project.memcache_port
        else:
            memcache_ip = '-'
            memcache_port = '-'
        if task.is_ssdb:
            ssdb_ip = task.project.ssdb_ip
            ssdb_port = task.project.ssdb_port
        else:
            ssdb_ip = '-'
            ssdb_port = '-'
        if task.is_kafka:
            kafka_ip = task.project.kafka_ip
            kafka_port = task.project.kafka_port
        else:
            kafka_ip = '-'
            kafka_port = '-'
        if task.is_rabbitMQ:
            rabbitMQ_ip = task.project.rabbitMQ_ip
            rabbitMQ_port = task.project.rabbitMQ_port
        else:
            rabbitMQ_ip = '-'
            rabbitMQ_port = '-'
        return jsonify({
            "project_name": task.project_name,
            "git_url": task.git_url,
            "host_type": task.host_type,
            "applicant": task.applicant,
            "manager": task.manager,
            "publisher": task.publisher,
            "checker": task.checker,
            "check_status": task.check_status,
            "project_domain": task.project_domain if task.project_domain else '-',
            "online_time": task.online_time if task.online_time else '-',
            "create_time": datetime.datetime.strftime(task.create_time,'%Y-%m-%d %H:%M:%S') if task.create_time else '-',
            "is_test": task.is_test,
            "emergent": task.emergent if task.emergent else '-',
            "start_command": task.start_command if task.start_command else '-',
            "start_port": task.start_port if task.start_port else '-',
            "is_public": task.is_public,
            "is_nginx": task.is_nginx,
            "is_crossdomain": task.is_crossdomain,
            "is_mysql": task.is_mysql,
            "is_postgresql": task.is_postgresql,
            'db_ip': db_ip,
            'db_name': db_name,
            "is_redis": task.is_redis,
            "redis_prefix": task.redis_prefix if task.redis_prefix else '-',
            'redis_ip': redis_ip,
            'redis_port': redis_port,
            "is_memcache": task.is_memcache,
            "memcache_prefix": task.memcache_prefix if task.memcache_prefix else '-',
            'memcache_ip': memcache_ip,
            'memcache_port': memcache_port,
            "is_ssdb": task.is_ssdb,
            "ssdb_prefix": task.ssdb_prefix if task.ssdb_prefix else '-',
            'ssdb_ip': ssdb_ip,
            'ssdb_port': ssdb_port,
            "is_kafka": task.is_kafka,
            "kafka_prefix": task.kafka_prefix if task.kafka_prefix else '-',
            'kafka_ip': kafka_ip,
            'kafka_port': kafka_port,
            "is_rabbitMQ": task.is_rabbitMQ,
            'rabbitMQ_ip': rabbitMQ_ip,
            'rabbitMQ_port': rabbitMQ_port,
            "host_configuration": task.host_configuration if task.host_configuration else '-',
            'host_ip': task.project.host_ip if task.project.host_ip else '-',
            "is_daemon": task.is_daemon,
            "daemon_mode": task.daemon_mode if task.daemon_mode else '-',
            "is_test_url": task.is_test_url,
            "test_url": task.test_url if task.test_url else '-',
            "is_slb": task.is_slb,
            "ha_special": task.ha_special if task.ha_special else '-',
            "service_type": task.service_type if task.service_type else '-',
            "is_log": task.is_log,
            "log_position": task.log_position if task.log_position else '-',
            "log_special_position": task.log_special_position if task.log_special_position else '-',
            "is_log_cut": task.is_log_cut,
            "log_clear": task.log_clear if task.log_clear else '-',
            "attachment": attachment if task.attachment else '-',
            "comment": task.comment if task.comment else '-',
            "is_front_cdn": task.project.is_front_cdn,
            "is_back_cdn": task.project.is_back_cdn,
            "front_cache_method": task.project.front_cache_method if task.project.front_cache_method else '-',
            "back_cache_method": task.project.back_cache_method if task.project.back_cache_method else '-',
            "front_cdn_manufacturer": task.project.front_cdn_manufacturer if task.project.front_cdn_manufacturer else '-',
            "back_cdn_manufacturer": task.project.back_cdn_manufacturer if task.project.back_cdn_manufacturer else '-',
        })
    return render_template('task/list_task.html', completed_tasks=completed_tasks, menu='completed_task_list',pagination=pagination)

@task.route('/task/operator/',methods = ['GET','POST'])
@login_required
def task_operator():
    task_id = request.form.get('task_id','')
    type = request.form.get('type','')
    data = request.form.get('data','')
    username = session.get('username')
    if session.get('role') == 'admin':
        unoperatored_tasks = Task.query.filter(Task.check_status == u'通过')
    else:
        unoperatored_tasks = Task.query.filter(Task.publisher == username,Task.check_status == u'通过')
    if task_id and not type and not data:
        task = Task.query.get(task_id)
        return jsonify({
            'is_mysql': task.is_mysql,
            'is_postgresql': task.is_postgresql,
            'is_redis': task.is_redis,
            'is_memcache': task.is_memcache,
            'is_ssdb': task.is_ssdb,
            'is_kafka': task.is_kafka,
            'is_rabbitMQ': task.is_rabbitMQ,
        })
    elif task_id and data:
        json_data = json.loads(data)
        is_exists = Project.query.filter(Project.task_id == task_id).first()
        if is_exists:
            p = Project.query.filter(Project.task_id == task_id).first()
        else:
            p = Project()
        p.is_front_cdn = True if json_data.get('is_front_cdn', '0') == '1' else False
        p.is_back_cdn = True if json_data.get('is_back_cdn', '0') == '1' else False
        p.front_cache_method = json_data.get('front_cache_method','')
        p.back_cache_method = json_data.get('back_cache_method','')
        p.front_cdn_manufacturer = json_data.get('front_cdn_manufacturer','')
        p.back_cdn_manufacturer = json_data.get('back_cdn_manufacturer','')
        p.host_ip = json_data.get('host_ip','')
        p.db_ip = json_data.get('db_ip','')
        p.db_name = json_data.get('db_name','')
        p.redis_ip = json_data.get('redis_ip','')
        p.redis_port = json_data.get('redis_port','')
        p.memcache_ip = json_data.get('memcache_ip','')
        p.memcache_port = json_data.get('memcache_port','')
        p.ssdb_ip = json_data.get('ssdb_ip','')
        p.ssdb_port = json_data.get('ssdb_port','')
        p.kafka_ip = json_data.get('kafka_ip','')
        p.kafka_port = json_data.get('kafka_port','')
        p.rabbitMQ_ip = json_data.get('rabbitMQ_ip','')
        p.rabbitMQ_port = json_data.get('rabbitMQ_port', '')
        p.comment = json_data.get('comment','')
        p.task_id = task_id
        db.session.merge(p)
        return jsonify({
            'result':1
        })
    elif task_id and type == 'finish':
        is_exists = Project.query.filter_by(task_id = task_id).first()
        if is_exists is None:
            return jsonify({
                'result':-1,
                'errMsg':u'请将项目信息补充完整！'
            })
        task = Task.query.get(task_id)
        tf = TaskFlow()
        task.check_status = u'完成'
        tf.task_name = task.project_name
        tf.operator = session.get('username')
        tf.applicant = task.applicant
        tf.task_status = u'完成'
        tf.task_id = task_id
        db.session.merge(task)
        db.session.add(tf)
        applicant = task.applicant
        user = User.query.filter_by(name = applicant).first()
        email = user.email
        mail.send_mail(u'项目上线完成通知', ['%s' % email], 'task_finish', applicant = applicant, project_name = task.project_name)
        return jsonify({
            'result':1
        })
    return render_template('task/operator_task.html',menu = 'operator_task_list',unoperatored_tasks = unoperatored_tasks)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

def split_str(str):
    return str[7:]
task.add_app_template_filter(split_str,'split_str')