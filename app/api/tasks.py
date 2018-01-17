# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 14:38
# @Author  : caoshuai
# @File    : tasks.py
# @Software: PyCharm

from flask import jsonify,abort,make_response,request,url_for,current_app
from authentication import auth
from . import api
from app import db
from app.task.models import Task
import datetime

@api.route('/api/tasks',methods = ['GET'])
@auth.login_required
def get_tasks():
    page = request.args.get('page', 1, type=int)
    pagination = Task.query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    tasks = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_tasks', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_tasks', page=page + 1, _external=True)
    task_list = []
    for task in tasks:
        task_list.append({
            'url': url_for('api.get_task', task_id = task.id, _external=True),
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
            'prev': prev,
            'next': next,
            'count': pagination.total,
        })
    return jsonify(task_list)

@api.route('/api/tasks/<int:task_id>',methods = ['GET'])
@auth.login_required
def get_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        abort(404)
    return jsonify({
        'url':url_for('api.get_task', task_id = task_id, _external=True),
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
        "create_time": datetime.datetime.strftime(task.create_time, '%Y-%m-%d %H:%M:%S') if task.create_time else '-',
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

@api.route('/api/tasks/<int:task_id>',methods = ['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        abort(404)
    db.session.delete(task)
    return jsonify({'result': True})

@api.route('/api/tasks',methods = ['POST'])
def create_task():
    pass

@api.route('/tasks/<int:task_id>',methods = ['PUT'])
def update_task(task_id):
    pass



