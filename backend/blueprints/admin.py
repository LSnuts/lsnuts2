import os
import functools
import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db, User, Post, Comment, Announcement

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

def admin_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return fail('请先登录', 401)
        if not current_user.is_admin:
            return fail('无权限', 403)
        return func(*args, **kwargs)
    return wrapper

@admin_bp.route('/api/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    res = [{'id': u.id, 'username': u.username, 'account_code': u.account_code, 'is_admin': u.is_admin, 'create_time': u.create_time.strftime('%Y-%m-%d %H:%M:%S')} for u in users]
    return ok(data=res)

@admin_bp.route('/api/admin/delete/<int:uid>', methods=['DELETE'])
@admin_required
def admin_delete(uid):
    if uid == current_user.id:
        return fail('不能删除自己')
    db.session.delete(User.query.get(uid))
    db.session.commit()
    return ok(msg='删除成功')

@admin_bp.route('/api/admin/reset_avatar/<int:uid>', methods=['POST'])
@admin_required
def admin_reset_avatar(uid):
    from app import app
    user = User.query.get(uid)
    if not user:
        return fail('用户不存在')
    
    if user.avatar:
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], user.avatar.replace('/uploads/', ''))
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
    
    user.avatar = None
    db.session.commit()
    
    return ok(msg='头像已重置为默认')

@admin_bp.route('/api/admin/update/<int:uid>', methods=['POST'])
@admin_required
def admin_update(uid):
    from utils import hash_password
    if uid == current_user.id:
        return fail('不能修改自己')
    
    data = request.json
    user = User.query.get(uid)
    
    if 'username' in data and data['username']:
        if User.query.filter(User.username == data['username'], User.id != uid).first():
            return fail('用户名已存在')
        user.username = data['username']
    
    if 'password' in data and data['password']:
        user.password = hash_password(data['password'])
    
    if 'is_admin' in data:
        user.is_admin = int(data['is_admin'])
    
    db.session.commit()
    return ok(msg='修改成功')

@admin_bp.route('/api/admin/posts')
@admin_required
def admin_posts():
    posts = db.session.query(Post, User.username).join(User, Post.user_id == User.id).order_by(Post.is_pinned.desc(), Post.create_time.desc()).all()
    res = []
    for post, username in posts:
        comment_count = db.session.query(Comment).filter(Comment.post_id == post.id).count()
        res.append({
            'id': post.id,
            'title': post.title,
            'user': username,
            'create_time': post.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'comment_count': comment_count,
            'is_pinned': post.is_pinned
        })
    return ok(data=res)

@admin_bp.route('/api/admin/delete_post/<int:post_id>', methods=['DELETE'])
@admin_required
def admin_delete_post(post_id):
    Comment.query.filter(Comment.post_id == post_id).delete()
    db.session.delete(Post.query.get(post_id))
    db.session.commit()
    return ok(msg='删除成功')

@admin_bp.route('/api/admin/toggle_pin/<int:post_id>', methods=['POST'])
@admin_required
def admin_toggle_pin(post_id):
    post = Post.query.get(post_id)
    if not post:
        return fail('帖子不存在')
    post.is_pinned = 1 if post.is_pinned == 0 else 0
    db.session.commit()
    status = '置顶' if post.is_pinned == 1 else '取消置顶'
    logger.info(f"[置顶] 管理员 {current_user.username} 将帖子 {post_id} {status}")
    return ok(msg=f'{status}成功', data={'is_pinned': post.is_pinned})

@admin_bp.route('/api/admin/stats')
@admin_required
def admin_stats():
    from sqlalchemy import func
    from models import Notification, File
    
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_files = File.query.count()
    total_notifications = Notification.query.count()
    
    today = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date()
    today_users = User.query.filter(func.date(User.create_time) == today).count()
    today_posts = Post.query.filter(func.date(Post.create_time) == today).count()
    today_comments = Comment.query.filter(func.date(Comment.create_time) == today).count()
    
    return ok(data={
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_files': total_files,
        'total_notifications': total_notifications,
        'today_users': today_users,
        'today_posts': today_posts,
        'today_comments': today_comments
    })

@admin_bp.route('/api/admin/announcements')
@admin_required
def admin_announcements():
    announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.create_time.desc()).all()
    res = [{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'priority': a.priority,
        'is_pinned': a.is_pinned,
        'create_time': a.create_time.strftime('%Y-%m-%d %H:%M:%S')
    } for a in announcements]
    return ok(data=res)

@admin_bp.route('/api/admin/announcement', methods=['POST'])
@admin_required
def admin_create_announcement():
    data = request.json
    if not data.get('title') or not data.get('content'):
        return fail('标题和内容不能为空')
    
    announcement = Announcement(
        title=data['title'],
        content=data['content'],
        priority=int(data.get('priority', 0)),
        is_pinned=int(data.get('is_pinned', 0))
    )
    db.session.add(announcement)
    db.session.commit()
    
    return ok(msg='公告发布成功', data={'id': announcement.id})

@admin_bp.route('/api/admin/announcement/<int:ann_id>', methods=['PUT'])
@admin_required
def admin_update_announcement(ann_id):
    announcement = Announcement.query.get(ann_id)
    if not announcement:
        return fail('公告不存在')
    
    data = request.json
    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'priority' in data:
        announcement.priority = int(data['priority'])
    if 'is_pinned' in data:
        announcement.is_pinned = int(data['is_pinned'])
    
    db.session.commit()
    return ok(msg='公告更新成功')

@admin_bp.route('/api/admin/announcement/<int:ann_id>', methods=['DELETE'])
@admin_required
def admin_delete_announcement(ann_id):
    announcement = Announcement.query.get(ann_id)
    if not announcement:
        return fail('公告不存在')
    
    db.session.delete(announcement)
    db.session.commit()
    return ok(msg='公告删除成功')

@admin_bp.route('/api/announcements/public')
def public_announcements():
    announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.create_time.desc()).limit(5).all()
    res = [{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'priority': a.priority,
        'is_pinned': a.is_pinned,
        'create_time': a.create_time.strftime('%Y-%m-%d %H:%M:%S')
    } for a in announcements]
    return ok(data=res)
