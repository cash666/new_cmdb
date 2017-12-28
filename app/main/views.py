# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 16:39
# @Author  : caoshuai
# @File    : views.py
# @Software: PyCharm Community Edition

from flask import render_template,session
from . import main
from flask_login import login_required
import datetime
from app.task.models import TaskFlow,Task
from app.auth.models import User
from app.asset.models import Asset
import json
from app import db
from sqlalchemy.sql import func

@main.route('/index')
@login_required
def index():
    user_count = User.query.filter(User.status == 1).count()
    asset_count = Asset.query.count()
    if session.get('role') == 'admin':
        uncheck_tasks = Task.query.filter(Task.check_status == u'待审核').count()
    else:
        uncheck_tasks = Task.query.filter(Task.check_status == u'待审核',Task.checker == session.get('username')).count()
    if session.get('role') == 'admin':
        unfinish_tasks = Task.query.filter(Task.check_status == u'通过').count()
    else:
        unfinish_tasks = Task.query.filter(Task.check_status == u'通过',Task.publisher == session.get('username')).count()
    apply_task_list = []
    finish_task_list = []
    today = datetime.date.today()
    date_list = [today - datetime.timedelta(days=6), today - datetime.timedelta(days=5),today - datetime.timedelta(days=4), today - datetime.timedelta(days=3),today - datetime.timedelta(days=2), today - datetime.timedelta(days=1), today]
    for date in date_list:
        apply_task_count = TaskFlow.query.filter(TaskFlow.task_status == u'待审核',TaskFlow.create_time.startswith('%s' % date)).count()
        finish_task_count = TaskFlow.query.filter(TaskFlow.task_status == u'完成', TaskFlow.create_time.startswith('%s' % date)).count()
        apply_task_list.append(int(apply_task_count))
        finish_task_list.append(int(finish_task_count))
    apply_task_user_top5 = []
    operate_task_user_top5 = []
    apply_task = db.session.query(TaskFlow.applicant,func.count(TaskFlow.task_name)).filter(TaskFlow.task_status == u'待审核').group_by(TaskFlow.applicant).order_by(func.count(TaskFlow.task_name).desc()).limit(5).all()
    operate_task = db.session.query(TaskFlow.operator,func.count(TaskFlow.task_name)).filter(TaskFlow.task_status == u'完成').group_by(TaskFlow.operator).order_by(func.count(TaskFlow.task_name).desc()).limit(5).all()
    for task in apply_task:
        applicant,count = task
        apply_task_user_top5.append({
            'applicant':applicant,
            'count':count
        })
    for task in operate_task:
        operator,count = task
        operate_task_user_top5.append({
            'operator':operator,
            'count':count
        })
    return render_template('index.html',apply_task_list = json.dumps(apply_task_list),finish_task_list = json.dumps(finish_task_list),user_count = user_count,asset_count = asset_count,uncheck_tasks = uncheck_tasks,unfinish_tasks = unfinish_tasks,apply_task_user_top5 = apply_task_user_top5,operate_task_user_top5 = operate_task_user_top5)