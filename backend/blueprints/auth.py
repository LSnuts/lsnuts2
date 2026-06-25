import os
import uuid
import random
import string
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import select, func

from models import db, User, Post, Comment, Bookmark, PostLike
from utils import hash_password, verify_password
from utils.secure_logger import info as secure_info, warning as secure_warning
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

def generate_account_code():
    while True:
        code = ''.join(random.choices(string.digits, k=6))
        if not User.query.filter_by(account_code=code).first():
            return code

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    secure_info(f"[登录] 收到登录请求", request.json)
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        secure_warning(f"[登录] 失败 - 用户不存在: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '该用户还未注册'})
    if not verify_password(data['password'], user.password):
        secure_warning(f"[登录] 失败 - 密码错误: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '密码错误'})
    login_user(user)
    secure_info(f"[登录] 成功 - 用户: {user.username} (ID:{user.id}), 账号码: {user.account_code}")
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {
        'id': user.id, 'username': user.username, 'account_code': user.account_code, 'is_admin': user.is_admin
    }})

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    secure_info(f"[注册] 收到注册请求", request.json)
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        secure_warning(f"[注册] 失败 - 用户名已存在: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '用户名已存在'})
    account_code = generate_account_code()
    user = User(username=data['username'], account_code=account_code, password=hash_password(data['password']))
    db.session.add(user)
    db.session.commit()
    secure_info(f"[注册] 成功 - 用户: {user.username} (ID:{user.id}), 账号码: {account_code}")
    return jsonify({'code': 200, 'msg': '注册成功', 'data': {'account_code': account_code}})

@auth_bp.route('/api/logout')
@login_required
def api_logout():
    logout_user()
    return jsonify({'code': 200, 'msg': '退出成功'})

@auth_bp.route('/api/user/info')
@login_required
def user_info():
    return jsonify({'code': 200, 'data': {
        'id': current_user.id,
        'username': current_user.username,
        'account_code': current_user.account_code,
        'is_admin': current_user.is_admin,
        'create_time': current_user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'avatar': current_user.avatar
    }})

@auth_bp.route('/api/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    from app import app
    file = request.files.get('avatar')
    if not file or file.filename == '':
        return jsonify({'code': 400, 'msg': '请选择图片'})
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'code': 400, 'msg': '仅支持png、jpg、jpeg、gif格式'})
    
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:
        return jsonify({'code': 400, 'msg': '图片大小不能超过10M'})
    
    unique_name = f"avatar_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(avatar_path)
    
    current_user.avatar = f"/uploads/{unique_name}"
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '上传成功', 'data': {'avatar': current_user.avatar}})

@auth_bp.route('/api/user/username', methods=['PUT'])
@login_required
def update_username():
    data = request.json
    new_username = data.get('username', '').strip()
    if not new_username or len(new_username) < 2 or len(new_username) > 20:
        return jsonify({'code': 400, 'msg': '用户名需2-20个字符'})
    existing = User.query.filter(User.username == new_username, User.id != current_user.id).first()
    if existing:
        return jsonify({'code': 400, 'msg': '该用户名已被占用'})
    current_user.username = new_username
    db.session.commit()
    return jsonify({'code': 200, 'msg': '用户名修改成功', 'data': {'username': new_username}})

@auth_bp.route('/api/user/password', methods=['PUT'])
@login_required
def update_password():
    data = request.json
    old_pw = data.get('old_password', '')
    new_pw = data.get('new_password', '')
    if not old_pw or not new_pw:
        return jsonify({'code': 400, 'msg': '新旧密码不能为空'})
    if len(new_pw) < 6 or len(new_pw) > 30:
        return jsonify({'code': 400, 'msg': '新密码需6-30个字符'})
    if not verify_password(old_pw, current_user.password):
        return jsonify({'code': 400, 'msg': '旧密码不正确'})
    current_user.password = hash_password(new_pw)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '密码修改成功'})

@auth_bp.route('/api/user/posts')
@login_required
def user_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    comment_count_subq = select(Comment.post_id, func.count(Comment.id).label('count')).group_by(Comment.post_id).subquery()
    like_count_subq = select(PostLike.post_id, func.count(PostLike.id).label('count')).group_by(PostLike.post_id).subquery()
    bookmarked_subq = select(Bookmark.post_id).filter(Bookmark.user_id == current_user.id).subquery()
    
    query = db.session.query(
        Post,
        func.coalesce(comment_count_subq.c.count, 0).label('comment_count'),
        func.coalesce(like_count_subq.c.count, 0).label('like_count'),
        Post.id.in_(bookmarked_subq).label('bookmarked')
    ).outerjoin(comment_count_subq, Post.id == comment_count_subq.c.post_id)\
     .outerjoin(like_count_subq, Post.id == like_count_subq.c.post_id)\
     .filter(Post.user_id == current_user.id)\
     .order_by(Post.create_time.desc())
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    data = []
    for p, comment_count, like_count, bookmarked in items:
        data.append({
            'id': p.id, 'title': p.title, 'content': p.content[:200],
            'create_time': p.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'tag': p.tag or '', 'comment_count': comment_count, 'like_count': like_count,
            'bookmarked': bookmarked
        })
    return jsonify({'code': 200, 'data': data, 'total': total, 'page': page, 'per_page': per_page})

@auth_bp.route('/api/user/bookmarks')
@login_required
def user_bookmarks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    comment_count_subq = select(Comment.post_id, func.count(Comment.id).label('count')).group_by(Comment.post_id).subquery()
    like_count_subq = select(PostLike.post_id, func.count(PostLike.id).label('count')).group_by(PostLike.post_id).subquery()
    
    query = db.session.query(
        Bookmark,
        Post,
        User.username,
        func.coalesce(comment_count_subq.c.count, 0).label('comment_count'),
        func.coalesce(like_count_subq.c.count, 0).label('like_count')
    ).join(Post, Bookmark.post_id == Post.id)\
     .join(User, Post.user_id == User.id)\
     .outerjoin(comment_count_subq, Post.id == comment_count_subq.c.post_id)\
     .outerjoin(like_count_subq, Post.id == like_count_subq.c.post_id)\
     .filter(Bookmark.user_id == current_user.id)\
     .order_by(Bookmark.create_time.desc())
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    data = []
    for bm, p, username, comment_count, like_count in items:
        data.append({
            'id': p.id, 'title': p.title, 'user': username,
            'create_time': p.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'tag': p.tag or '', 'comment_count': comment_count, 'like_count': like_count,
            'bookmark_id': bm.id, 'bookmark_time': bm.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'code': 200, 'data': data, 'total': total, 'page': page, 'per_page': per_page})

@auth_bp.route('/api/user/search')
@login_required
def search_user():
    keyword = request.args.get('keyword', '') or request.args.get('q', '')
    
    query = User.query.filter(User.id != current_user.id)
    if keyword:
        query = query.filter(
            (User.username.like(f'%{keyword}%')) |
            (User.account_code == keyword) |
            (User.id == int(keyword) if keyword.isdigit() else False)
        )
    users = query.limit(10).all()
    
    data = [{
        'id': u.id,
        'username': u.username,
        'account_code': u.account_code,
        'is_admin': u.is_admin
    } for u in users]
    
    return jsonify({'code': 200, 'data': data})

@auth_bp.route('/api/user/list')
@login_required
def user_list():
    users = User.query.filter(User.id != current_user.id).all()
    data = [{
        'id': u.id,
        'username': u.username,
        'account_code': u.account_code,
        'is_admin': u.is_admin
    } for u in users]
    return jsonify({'code': 200, 'data': data})

@auth_bp.route('/api/user/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'})
    
    post_count = Post.query.filter_by(user_id=user_id).count()
    comment_count = Comment.query.filter_by(user_id=user_id).count()
    
    return jsonify({'code': 200, 'data': {
        'id': user.id,
        'username': user.username,
        'avatar': user.avatar,
        'create_time': user.create_time.strftime('%Y-%m-%d'),
        'is_admin': user.is_admin,
        'post_count': post_count,
        'comment_count': comment_count
    }})

@auth_bp.route('/api/user/profile/<int:user_id>/posts')
def user_profile_posts(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'})
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Post.query.filter_by(user_id=user_id).order_by(Post.create_time.desc())
    total = query.count()
    posts = query.offset((page - 1) * per_page).limit(per_page).all()
    
    data = [{
        'id': p.id,
        'title': p.title,
        'content': p.content[:200],
        'tag': p.tag or '',
        'create_time': p.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'comment_count': Comment.query.filter_by(post_id=p.id).count(),
        'like_count': PostLike.query.filter_by(post_id=p.id).count()
    } for p in posts]
    
    return jsonify({'code': 200, 'data': data, 'total': total, 'page': page, 'per_page': per_page})

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    from datetime import timedelta
    
    data = request.json
    username = data.get('username', '').strip()
    account_code = data.get('account_code', '').strip()
    
    if not username or not account_code:
        return jsonify({'code': 400, 'msg': '用户名和账号码不能为空'})
    
    user = User.query.filter_by(username=username, account_code=account_code).first()
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在或账号码错误'})
    
    token = uuid.uuid4().hex
    user.reset_token = token
    user.reset_expire = datetime.now(timezone.utc) + timedelta(hours=1)
    db.session.commit()
    
    reset_url = f"/reset-password?token={token}"
    return jsonify({'code': 200, 'msg': '验证成功，请设置新密码', 'data': {'reset_url': reset_url}})

@auth_bp.route('/api/auth/verify-token', methods=['GET'])
def verify_token():
    token = request.args.get('token', '')
    if not token:
        return jsonify({'code': 400, 'msg': 'token不能为空'})
    
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'code': 404, 'msg': 'token无效'})
    
    if user.reset_expire and user.reset_expire < datetime.now(timezone.utc):
        return jsonify({'code': 410, 'msg': 'token已过期，请重新申请'})
    
    return jsonify({'code': 200, 'msg': 'token有效', 'data': {'username': user.username}})

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    
    if not token or not new_password:
        return jsonify({'code': 400, 'msg': 'token和新密码不能为空'})
    
    if len(new_password) < 6 or len(new_password) > 30:
        return jsonify({'code': 400, 'msg': '密码需6-30个字符'})
    
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'code': 404, 'msg': 'token无效'})
    
    if user.reset_expire and user.reset_expire < datetime.now(timezone.utc):
        return jsonify({'code': 410, 'msg': 'token已过期，请重新申请'})
    
    user.password = hash_password(new_password)
    user.reset_token = None
    user.reset_expire = None
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '密码重置成功，请使用新密码登录'})
