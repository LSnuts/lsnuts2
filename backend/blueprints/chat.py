import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db, Message, User, Friendship

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
    
    query = db.session.query(Message, User.username, User.avatar).join(User, Message.sender_id == User.id).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.send_time.asc())
    
    total = query.count()
    
    messages = query.offset(offset).limit(limit).all()
    
    data = []
    for msg, sender_name, sender_avatar in messages:
        data.append({
            'sender_id': msg.sender_id,
            'sender': sender_name,
            'sender_avatar': sender_avatar,
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
    
    try:
        notifs = Notification.query.filter(Notification.user_id == current_user.id).order_by(Notification.create_time.desc()).limit(50).all()
    except Exception as e:
        logger.error(f"查询通知失败: {e}")
        return jsonify({'code': 200, 'data': []})
    
    data = []
    for n in notifs:
        username = '未知用户'
        avatar = None
        post_title = None
        comment_content = None
        message_content = None
        
        if n.comment_id:
            comment = Comment.query.get(n.comment_id)
            if comment:
                comment_user = User.query.get(comment.user_id)
                if comment_user:
                    username = comment_user.username
                    avatar = comment_user.avatar
                comment_content = comment.content[:100]
        
        if n.post_id:
            post = Post.query.get(n.post_id)
            if post:
                post_title = post.title
        
        item = {
            'id': n.id,
            'post_id': n.post_id,
            'comment_id': n.comment_id,
            'message_id': None,
            'sender_id': None,
            'type': n.type or 'comment_reply',
            'is_read': n.is_read,
            'create_time': n.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'username': username,
            'avatar': avatar,
            'post_title': post_title or '(帖子已删除)',
            'post_deleted': post_title is None,
            'comment_content': comment_content,
            'message_content': message_content
        }
        
        data.append(item)
    
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

@chat_bp.route('/api/users/online')
@login_required
def online_users():
    logger.info(f"[在线用户] 用户 {current_user.id} 请求在线用户列表")
    
    from app import online_users_sockets
    
    online_user_ids = set(online_users_sockets.keys())
    online_user_ids.discard(str(current_user.id))
    
    users = User.query.filter(User.id.in_([int(uid) for uid in online_user_ids])).all()
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'account_code': user.account_code,
            'avatar': user.avatar,
            'is_online': True
        })
    
    logger.info(f"[在线用户] 返回 {len(data)} 个在线用户")
    return jsonify({'code': 200, 'data': data})

@chat_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.commit()
    
    logger.info(f"[私聊消息] 用户 {current_user.id} -> 用户 {receiver_id}: {content[:50]}")
    
    return jsonify({'code': 200, 'msg': '发送成功', 'data': {
        'sender': current_user.username,
        'sender_id': current_user.id,
        'content': content,
        'send_time': msg.send_time.strftime('%Y-%m-%d %H:%M:%S')
    }})

@chat_bp.route('/api/users/search')
@login_required
def search_users():
    query = request.args.get('q', '')
    logger.info(f"[搜索用户] 用户 {current_user.id} 搜索: {query}")
    
    if not query:
        return jsonify({'code': 200, 'data': []})
    
    users = User.query.filter(
        (User.username.like(f'%{query}%')) | (User.account_code.like(f'%{query}%'))
    ).all()
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'account_code': user.account_code,
            'avatar': user.avatar
        })
    
    logger.info(f"[搜索用户] 返回 {len(data)} 个结果")
    return jsonify({'code': 200, 'data': data})

@chat_bp.route('/api/friends/request', methods=['POST'])
@login_required
def send_friend_request():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    
    if user_id == current_user.id:
        return jsonify({'code': 400, 'msg': '不能添加自己'}), 400
    
    receiver = User.query.get(user_id)
    if not receiver:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    existing = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
        ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if existing:
        if existing.status == 1:
            return jsonify({'code': 400, 'msg': '已经是好友'}), 400
        elif existing.status == 0:
            return jsonify({'code': 400, 'msg': '请求已发送'}), 400
        elif existing.status == 2:
            existing.status = 0
            existing.create_time = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"[好友请求] 用户 {current_user.id} 重新发送请求给用户 {user_id}")
            return jsonify({'code': 200, 'msg': '好友请求已发送'})
    
    friendship = Friendship(user_id=current_user.id, friend_id=user_id, status=0)
    db.session.add(friendship)
    db.session.commit()
    
    logger.info(f"[好友请求] 用户 {current_user.id} 发送请求给用户 {user_id}")
    return jsonify({'code': 200, 'msg': '好友请求已发送'})

@chat_bp.route('/api/friends/list')
@login_required
def friend_list():
    logger.info(f"[好友列表] 用户 {current_user.id} 请求好友列表")
    
    friends = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)) &
        (Friendship.status == 1)
    ).all()
    
    friend_ids = []
    for f in friends:
        if f.user_id == current_user.id:
            friend_ids.append(f.friend_id)
        else:
            friend_ids.append(f.user_id)
    
    users = User.query.filter(User.id.in_(friend_ids)).all()
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'account_code': user.account_code,
            'avatar': user.avatar
        })
    
    logger.info(f"[好友列表] 返回 {len(data)} 个好友")
    return jsonify({'code': 200, 'data': data})

@chat_bp.route('/api/friends/pending')
@login_required
def pending_requests():
    logger.info(f"[待处理请求] 用户 {current_user.id} 请求待处理列表")
    
    pending = Friendship.query.filter(
        Friendship.friend_id == current_user.id,
        Friendship.status == 0
    ).all()
    
    user_ids = [p.user_id for p in pending]
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'account_code': user.account_code,
            'avatar': user.avatar
        })
    
    logger.info(f"[待处理请求] 返回 {len(data)} 个待处理请求")
    return jsonify({'code': 200, 'data': data})

@chat_bp.route('/api/friends/accept', methods=['POST'])
@login_required
def accept_friend_request():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    
    friendship = Friendship.query.filter(
        Friendship.user_id == user_id,
        Friendship.friend_id == current_user.id,
        Friendship.status == 0
    ).first()
    
    if not friendship:
        return jsonify({'code': 404, 'msg': '请求不存在'}), 404
    
    friendship.status = 1
    db.session.commit()
    
    logger.info(f"[好友接受] 用户 {current_user.id} 接受用户 {user_id} 的好友请求")
    return jsonify({'code': 200, 'msg': '已添加好友'})

@chat_bp.route('/api/friends/reject', methods=['POST'])
@login_required
def reject_friend_request():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    
    friendship = Friendship.query.filter(
        Friendship.user_id == user_id,
        Friendship.friend_id == current_user.id,
        Friendship.status == 0
    ).first()
    
    if not friendship:
        return jsonify({'code': 404, 'msg': '请求不存在'}), 404
    
    friendship.status = 2
    db.session.commit()
    
    logger.info(f"[好友拒绝] 用户 {current_user.id} 拒绝用户 {user_id} 的好友请求")
    return jsonify({'code': 200, 'msg': '已拒绝'})
