import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db, Message, User

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

@chat_bp.route('/api/chat/history/<int:other_id>')
@login_required
def chat_history(other_id):
    logger.info(f"[聊天记录] 用户 {current_user.id} 请求与用户 {other_id} 的聊天记录")
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = db.session.query(Message, User.username).join(User, Message.sender_id == User.id).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.send_time.asc())
    
    total = query.count()
    
    messages = query.offset(offset).limit(limit).all()
    
    data = []
    for msg, sender_name in messages:
        data.append({
            'sender_id': msg.sender_id,
            'sender': sender_name,
            'content': msg.content,
            'send_time': msg.send_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    logger.info(f"[聊天记录] 返回 {len(data)}/{total} 条消息")
    return jsonify({'code': 200, 'data': data, 'total': total, 'limit': limit, 'offset': offset})

@chat_bp.route('/api/notifications/count')
@login_required
def notification_count():
    from models import Notification
    count = Notification.query.filter_by(user_id=current_user.id, is_read=0).count()
    return jsonify({'code': 200, 'data': {'count': count}})

@chat_bp.route('/api/notifications')
@login_required
def notification_list():
    from models import Notification, Post, Comment
    notifs = db.session.query(Notification, Post.title, Comment.content, User.username).outerjoin(Post, Notification.post_id == Post.id).join(Comment, Notification.comment_id == Comment.id).join(User, Comment.user_id == User.id).filter(Notification.user_id == current_user.id).order_by(Notification.create_time.desc()).limit(50).all()
    data = []
    for n, post_title, comment_content, replier in notifs:
        data.append({
            'id': n.id,
            'post_id': n.post_id,
            'comment_id': n.comment_id,
            'post_title': post_title or '(帖子已删除)',
            'post_deleted': post_title is None,
            'comment_content': (comment_content or '')[:100],
            'replier': replier,
            'type': n.type or 'comment_reply',
            'is_read': n.is_read,
            'create_time': n.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'code': 200, 'data': data})

@chat_bp.route('/api/notifications/read', methods=['POST'])
@login_required
def notification_read():
    from models import Notification
    Notification.query.filter_by(user_id=current_user.id, is_read=0).update({'is_read': 1})
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已全部标记为已读'})

@chat_bp.route('/api/notifications/<int:notif_id>', methods=['DELETE'])
@login_required
def notification_delete(notif_id):
    from models import Notification
    n = Notification.query.get(notif_id)
    if not n or n.user_id != current_user.id:
        return jsonify({'code':404, 'msg':'通知不存在'})
    db.session.delete(n)
    db.session.commit()
    return jsonify({'code':200, 'msg':'已删除'})
