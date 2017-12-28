# -*- coding: utf-8 -*-
# @Time    : 2017/11/27 9:57
# @Author  : caoshuai
# @File    : views.py
# @Software: PyCharm Community Edition

from flask import render_template,redirect,url_for,request,jsonify,current_app,session
from flask_login import login_user,logout_user,login_required
from . import auth
from .models import User,Role,Permission,role_permission
from sqlalchemy import not_,or_
from app import db
from app.utils import mail
import json

@auth.route('/login', methods = ['GET','POST'])
def login():
    username = request.form.get('username','')
    password = request.form.get('password','')
    remember_me = request.form.get('remember_me',False)
    next = request.args.get('next', '')
    if username and password:
        user = User.query.filter_by(name = username).first()
        if user is not None and user.verify_password(password):
            if user.status == 0:
                return jsonify({
                    'result': -1,
                    'errMsg': u'用户已被禁用，请联系管理员解除禁用！'
                })
            else:
                login_user(user, remember_me)
                session['username'] = username
                session['role'] = user.role.name
                return jsonify({
                    'result':1,
                    'next':next
                })
        else:
            return jsonify({
                'result': -1,
                'errMsg': u'用户名或者密码错误！'
            })
    return render_template('auth/login.html')

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/user/list/',methods=['GET','POST'])
@login_required
def list_user():
    role_id = request.form.get('role_id', '')
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = request.form.get('email', '')
    status = request.form.get('status', '')
    new_password = request.form.get('new_password','')
    sort = request.form.get('sort','')
    page = request.args.get('page', 1, type=int)
    type = request.form.get('type','')
    pagination = User.query.paginate(page, per_page=current_app.config['PER_PAGE'],error_out=False)
    users = pagination.items
    if role_id and username and password and email and status:
        is_exists = User.query.filter_by(name = username,email = email).first()
        status = True if int(status) == 1 else False
        if is_exists:
            return jsonify({
                'result':-1,
                'errMsg':u'用户已存在!',
            })
        u = User()
        u.name = username
        u.password = password
        u.email = email
        u.status = status
        u.role_id = role_id
        db.session.add(u)
        mail.send_mail(u'CMDB系统账号开通通知',['%s' % email],'register',username = username,password = password)
        return jsonify({
            'result':1
        })
    elif user_id and username and email and role_id and not password and not status:
        user = User.query.filter_by(id = user_id, name = username, email = email, role_id = role_id).first()
        if user is None:
            u = User.query.get(user_id)
            u.username = username
            u.email = email
            u.role_id = role_id
            db.session.merge(u)
            return jsonify({
                'result':1
            })
    elif user_id and not status and not new_password:
        u = User.query.get(user_id)
        db.session.delete(u)
        return jsonify({
            'result':1
        })
    elif user_id and status:
        status = True if int(status) == 1 else False
        u = User.query.get(user_id)
        u.status = status
        db.session.merge(u)
        return jsonify({
            'result': 1
        })
    elif user_id and new_password:
        u = User.query.get(user_id)
        u.password = new_password
        db.session.merge(u)
        return jsonify({
            'result': 1
        })
    elif type == 'task':
        user_list = []
        users = User.query.all()
        for u in users:
            user_list.append({
                'id': u.id,
                'name': u.name,
            })
        return jsonify(user_list)
    return render_template('auth/users.html',users = users,menu = 'user_list',pagination = pagination,sort = sort)

@auth.route('/role/list/',methods=['GET','POST'])
@login_required
def list_role():
    role_id = request.form.get('role_id','')
    type = request.form.get('type','')
    role_name = request.form.get('role_name','')
    all = request.form.get('all','')
    grant_list = request.form.get('grant_list','')
    page = request.args.get('page', 1, type=int)
    pagination = Role.query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    roles = pagination.items
    if all:
        result = []
        for r in roles:
            result.append({
                'role_id':r.id,
                'role_name':r.name,
            })
        return jsonify(result)
    elif role_id and grant_list:
        grant_list_json = json.loads(grant_list)
        r = Role.query.get(role_id)
        permissions = r.permissions.all()
        if permissions:
            for p in permissions:
                r.permissions.remove(p)
                db.session.add(r)
        for p_id in grant_list_json:
            p = Permission.query.get(p_id)
            r.permissions.append(p)
            db.session.add(r)
        return jsonify({
            'result':1
        })
    elif role_id and not type:
        permissions_list = []
        permission_id_list = []
        rp = db.session.query(role_permission).filter_by(role_id = role_id)
        for p in rp:
            permission_id_list.append(p.permission_id)
            permission = Permission.query.get(p.permission_id)
            permissions_list.append({
                'role_id':role_id,
                'permission_id':p.permission_id,
                'permission_name':permission.name,
                'permission_alias_name':permission.alias_name,
                'permission_rw':2,
            })
        permission = Permission.query.filter(not_(Permission.id.in_(permission_id_list)))
        for p in permission:
            permissions_list.append({
                'role_id': role_id,
                'permission_id': p.id,
                'permission_name': p.name,
                'permission_alias_name': p.alias_name,
                'permission_rw': 0,
            })
        return jsonify(permissions_list)
    elif role_id and type:
        role = Role.query.get(role_id)
        db.session.delete(role)
        return jsonify({
            'result': 1
        })
    elif role_name:
        r = Role()
        r.name = role_name
        db.session.add(r)
        return jsonify({
            'result':1
        })
    return render_template('auth/roles.html',roles = roles,menu = 'role_list',pagination = pagination)

@auth.route('/permission/list/',methods=['GET','POST'])
@login_required
def list_permission():
    permission_name = request.form.get('permission_name','')
    permission_alias_name = request.form.get('permission_alias_name','')
    permission_id = request.form.get('permission_id','')
    type = request.form.get('type','')
    page = request.args.get('page', 1, type=int)
    pagination = Permission.query.paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    permissions = pagination.items
    if permission_id and not type:
        p = Permission.query.get(permission_id)
        db.session.delete(p)
        return jsonify({
            'result':1
        })
    elif permission_name and permission_alias_name and not type:
        is_exists = Permission.query.filter(or_(Permission.name == permission_name,Permission.alias_name == permission_alias_name)).first()
        if is_exists is not None:
            return jsonify({
                'result':-1,
                'errMsg':u'权限名称或者权限说明已经存在，请重新添加！',
            })
        else:
            p = Permission()
            p.name = permission_name
            p.alias_name = permission_alias_name
            db.session.add(p)
            return jsonify({
                'result':1
            })
    elif permission_id and permission_name and permission_alias_name and type == 'modify':
        p = Permission.query.get(permission_id)
        p.name = permission_name
        p.alias_name = permission_alias_name
        db.session.merge(p)
        return jsonify({
            'result':1
        })
    return render_template('auth/permission.html', permissions = permissions,menu = 'permission_list', pagination = pagination)