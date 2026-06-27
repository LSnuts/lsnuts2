import os
import uuid
import re
import logging
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import select, func

from models import db, Post, Comment, User, PostLike, Bookmark, Notification
from werkzeug.utils import secure_filename

forum_bp = Blueprint('forum', __name__)
logger = logging.getLogger(__name__)

def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

@forum_bp.route('/api/forum/list')
def forum_list():
    logger.info(f"[论坛列表] 收到请求 - 搜索:{request.args.get('search','')} 页码:{request.args.get('page','1')} 标签:{request.args.get('tag','')}")
    
    search = request.args.get('search', '').strip()
    tag = request.args.get('tag', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    comment_count_subq = select(Comment.post_id, func.count(Comment.id).label('count')).group_by(Comment.post_id).subquery()
    like_count_subq = select(PostLike.post_id, func.count(PostLike.id).label('count')).group_by(PostLike.post_id).subquery()
    
    user_post_count_subq = select(Post.user_id, func.count(Post.id).label('count')).group_by(Post.user_id).subquery()
    
    query = db.session.query(
        Post, 
        User.username, 
        User.is_admin, 
        User.avatar,
        func.coalesce(comment_count_subq.c.count, 0).label('comment_count'),
        func.coalesce(like_count_subq.c.count, 0).label('like_count'),
        func.coalesce(user_post_count_subq.c.count, 0).label('user_post_count'),
        User.create_time.label('user_created')
    ).join(User, Post.user_id == User.id)\
     .outerjoin(comment_count_subq, Post.id == comment_count_subq.c.post_id)\
     .outerjoin(like_count_subq, Post.id == like_count_subq.c.post_id)\
     .outerjoin(user_post_count_subq, Post.user_id == user_post_count_subq.c.user_id)
    
    if search:
        query = query.filter(db.or_(Post.title.contains(search), Post.content.contains(search)))
    
    if tag:
        if tag == 'other':
            query = query.filter((Post.tag == None) | (Post.tag == '') | (Post.tag == 'other'))
        else:
            query = query.filter(Post.tag == tag)
    
    query = query.order_by(Post.is_pinned.desc(), Post.create_time.desc())
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    data = []
    for post, username, is_admin, avatar, comment_count, like_count, user_post_count, user_created in items:
        data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
            'user': username,
            'is_admin': is_admin,
            'avatar': avatar,
            'create_time': post.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'comment_count': comment_count,
            'like_count': like_count,
            'is_pinned': post.is_pinned,
            'tag': post.tag or '',
            'image': post.image,
            'user_post_count': user_post_count,
            'user_created': user_created.strftime('%Y-%m-%d')
        })
    logger.info(f"[论坛列表] 返回 {len(data)}/{total} 条帖子数据")
    return jsonify({'code':200, 'data':data, 'total': total, 'page': page, 'per_page': per_page})

@forum_bp.route('/api/forum/post', methods=['POST'])
@login_required
def forum_post():
    from app import app
    logger.info(f"[论坛发帖] 收到请求 - 用户: {current_user.username} (ID:{current_user.id})")
    
    if request.is_json:
        title = request.json.get('title', '')
        content = request.json.get('content', '')
        tag = request.json.get('tag', '')
    else:
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        tag = request.form.get('tag', '')
    logger.info(f"[论坛发帖] 请求数据: title={title}, content_len={len(content)}")
    
    if not title or not content:
        logger.warning(f"[论坛发帖] 失败 - 标题或内容为空")
        return jsonify({'code':400, 'msg':'标题和内容不能为空'})
    
    post = Post(title=title, content=content, user_id=current_user.id, tag=tag if tag else None)
    
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            img_name = f"post_image_{uuid.uuid4().hex}.{ext}"
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            image_file.save(img_path)
            post.image = f"/uploads/{img_name}"
            logger.info(f"[论坛发帖] 图片已保存: {img_name}")
    
    attach_file = request.files.get('attachment')
    if attach_file and attach_file.filename:
        original_name = secure_filename(attach_file.filename)
        store_name = f"post_attach_{uuid.uuid4().hex}_{original_name}"
        attach_path = os.path.join(app.config['UPLOAD_FOLDER'], store_name)
        attach_file.save(attach_path)
        post.attachment_name = original_name
        post.attachment_path = f"/uploads/{store_name}"
        logger.info(f"[论坛发帖] 附件已保存: {original_name}")
    
    db.session.add(post)
    db.session.commit()
    
    logger.info(f"[论坛发帖] 成功 - 帖子ID:{post.id}, 标题:{title}")
    return jsonify({'code':200, 'msg':'发布成功', 'data': {'id': post.id}})

@forum_bp.route('/api/forum/detail/<int:post_id>')
def forum_detail(post_id):
    post_data = db.session.query(Post, User.username, User.is_admin, User.avatar, User.create_time).join(User, Post.user_id == User.id).filter(Post.id == post_id).first()
    if not post_data:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    post, post_username, post_is_admin, post_avatar, user_created = post_data
    
    user_post_count = Post.query.filter_by(user_id=post.user_id).count()
    
    like_count = PostLike.query.filter_by(post_id=post_id).count()
    user_liked = False
    user_bookmarked = False
    if current_user.is_authenticated:
        user_liked = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
        user_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    
    all_comments = db.session.query(Comment, User.username, User.is_admin, User.avatar, User.create_time).join(User, Comment.user_id == User.id).filter(Comment.post_id == post_id).order_by(Comment.create_time.asc()).all()
    
    comment_map = {}
    top_comments = []
    for comment, username, is_admin, avatar, c_user_created in all_comments:
        c = {
            'id': comment.id,
            'content': comment.content,
            'user': username,
            'is_admin': is_admin,
            'avatar': avatar,
            'parent_id': comment.parent_id,
            'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'replies': [],
            'user_post_count': Post.query.filter_by(user_id=comment.user_id).count(),
            'user_created': c_user_created.strftime('%Y-%m-%d') if c_user_created else ''
        }
        comment_map[comment.id] = c
        if comment.parent_id:
            if comment.parent_id in comment_map:
                comment_map[comment.parent_id]['replies'].append(c)
        else:
            top_comments.append(c)
    
    return jsonify({'code':200, 'data':{'post':{
        'id': post.id, 'title': post.title, 'content': post.content, 'user': post_username, 'user_id': post.user_id, 'is_admin': post_is_admin, 'avatar': post_avatar, 'create_time': post.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'tag': post.tag or '', 'edit_count': post.edit_count or 0, 'last_edit_time': post.last_edit_time.strftime('%Y-%m-%d %H:%M:%S') if post.last_edit_time else None,
        'like_count': like_count, 'user_liked': user_liked, 'user_bookmarked': user_bookmarked,
        'image': post.image, 'attachment_name': post.attachment_name, 'attachment_path': post.attachment_path,
        'user_post_count': user_post_count,
        'user_created': user_created.strftime('%Y-%m-%d') if user_created else ''
    }, 'current_user_id': current_user.id if current_user.is_authenticated else None, 'comments': top_comments}})

@forum_bp.route('/api/forum/comment/<int:post_id>', methods=['POST'])
@login_required
def forum_comment(post_id):
    logger.info(f"[论坛评论] 收到请求 - 用户: {current_user.username} (ID:{current_user.id}), 帖子ID: {post_id}")
    data = request.json
    
    if not data.get('content'):
        logger.warning(f"[论坛评论] 失败 - 评论内容为空")
        return jsonify({'code':400, 'msg':'评论内容不能为空'})
    
    parent_id = data.get('parent_id')
    
    comment = Comment(content=data['content'], post_id=post_id, user_id=current_user.id, parent_id=parent_id)
    db.session.add(comment)
    
    post = Post.query.get(post_id)
    
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if parent_comment and parent_comment.user_id != current_user.id:
            notification = Notification(
                user_id=parent_comment.user_id,
                post_id=post_id,
                comment_id=comment.id,
                type='comment_reply'
            )
            db.session.add(notification)
            logger.info(f"[通知] 创建 comment_reply 通知给用户 {parent_comment.user_id}")
    else:
        if post and post.user_id != current_user.id:
            notification = Notification(
                user_id=post.user_id,
                post_id=post_id,
                comment_id=comment.id,
                type='post_reply'
            )
            db.session.add(notification)
            logger.info(f"[通知] 创建 post_reply 通知给用户 {post.user_id}")
    
    mentioned_users = re.findall(r'@(\w{2,20})', data['content'])
    if mentioned_users:
        mentioned_users = list(set(mentioned_users))
        for username in mentioned_users:
            user = User.query.filter_by(username=username).first()
            if user and user.id != current_user.id:
                if parent_id:
                    parent_comment = Comment.query.get(parent_id)
                    if parent_comment and user.id == parent_comment.user_id:
                        continue
                if post and user.id == post.user_id:
                    continue
                notification = Notification(
                    user_id=user.id,
                    post_id=post_id,
                    comment_id=comment.id,
                    type='mention'
                )
                db.session.add(notification)
                logger.info(f"[通知] 创建 mention 通知给用户 {user.username}")
    
    db.session.commit()
    
    logger.info(f"[论坛评论] 成功 - 评论ID: {comment.id}, 回复: {bool(parent_id)}")
    return jsonify({'code':200, 'msg':'回复成功' if parent_id else '评论成功', 'data': {'id': comment.id}})

@forum_bp.route('/api/forum/delete/<int:post_id>', methods=['DELETE'])
@login_required
def forum_delete(post_id):
    if current_user.is_admin != 1:
        return jsonify({'code':403, 'msg':'无权限'})
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    
    Comment.query.filter_by(post_id=post_id).delete()
    Notification.query.filter_by(post_id=post_id).delete()
    PostLike.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    
    logger.info(f"[论坛删帖] 管理员 {current_user.username} 删除帖子 {post_id}")
    return jsonify({'code':200, 'msg':'删除成功'})

@forum_bp.route('/api/forum/post/<int:post_id>', methods=['PUT'])
@login_required
def forum_edit(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    if post.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'只能编辑自己的帖子'})
    
    if datetime.now(timezone.utc) - post.create_time > timedelta(hours=24):
        return jsonify({'code':403, 'msg':'发表超过24小时无法编辑'})
    
    data = request.json
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    tag = data.get('tag', '')
    
    if not title or not content:
        return jsonify({'code':400, 'msg':'标题和内容不能为空'})
    
    post.title = title
    post.content = content
    post.tag = tag if tag and tag != 'other' else None
    post.edit_count = (post.edit_count or 0) + 1
    post.last_edit_time = datetime.now(timezone.utc)
    db.session.commit()
    
    logger.info(f"[论坛编辑] 用户 {current_user.username} 编辑帖子 {post_id}，编辑次数: {post.edit_count}")
    return jsonify({'code':200, 'msg':'编辑成功'})

@forum_bp.route('/api/forum/post/<int:post_id>', methods=['DELETE'])
@login_required
def forum_delete_own(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    if post.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'只能删除自己的帖子'})
    Comment.query.filter_by(post_id=post_id).delete()
    Notification.query.filter_by(post_id=post_id).delete()
    PostLike.query.filter_by(post_id=post_id).delete()
    Bookmark.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'code':200, 'msg':'删除成功'})

@forum_bp.route('/api/forum/like/<int:post_id>', methods=['POST'])
@login_required
def forum_like(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    
    existing = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        like_count = PostLike.query.filter_by(post_id=post_id).count()
        return jsonify({'code':200, 'msg':'已取消点赞', 'data': {'liked': False, 'like_count': like_count}})
    else:
        pl = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(pl)
        db.session.commit()
        like_count = PostLike.query.filter_by(post_id=post_id).count()
        return jsonify({'code':200, 'msg':'点赞成功', 'data': {'liked': True, 'like_count': like_count}})

@forum_bp.route('/api/forum/bookmark/<int:post_id>', methods=['POST'])
@login_required
def forum_bookmark(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    existing = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'code':200, 'msg':'已取消收藏', 'data': {'bookmarked': False}})
    else:
        bm = Bookmark(user_id=current_user.id, post_id=post_id)
        db.session.add(bm)
        db.session.commit()
        return jsonify({'code':200, 'msg':'收藏成功', 'data': {'bookmarked': True}})

@forum_bp.route('/api/forum/attachment/<int:post_id>')
@login_required
def forum_attachment_download(post_id):
    from app import app
    post = Post.query.get(post_id)
    if not post or not post.attachment_path:
        return jsonify({'code':400, 'msg':'附件不存在'})
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(post.attachment_path))
    if not os.path.exists(file_path):
        return jsonify({'code':400, 'msg':'附件文件不存在'})
    return send_file(file_path, as_attachment=True, download_name=post.attachment_name or 'attachment')
