import os  # 文件路径操作
import uuid  # 生成唯一文件名
import functools  # 装饰器工具

# 加载环境变量配置
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载 .env 文件中的环境变量
except ImportError:
    pass  # 如果没有安装 python-dotenv，忽略此步骤
import random  # 随机数生成
import re  # 正则表达式解析@提及
from sqlalchemy import select, func  # 子查询支持和聚合函数
import string  # 字符串工具
import logging  # 日志记录
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # 跨域支持
from flask_login import LoginManager, login_user, login_required, logout_user, current_user  # 用户登录管理
from flask_socketio import SocketIO, emit  # WebSocket实时通信
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, File, Message, Post, Comment, Notification, PostLike, Bookmark
from utils import hash_password, verify_password  # 密码加密工具
from utils.secure_logger import info as secure_info, warning as secure_warning  # 安全日志工具
from werkzeug.utils import secure_filename  # 安全文件名处理

# 配置日志格式：时间 - 级别 - 消息
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SECRET_KEY 持久化处理
def load_or_generate_secret_key():
    secret_key_path = os.path.join(os.path.dirname(__file__), 'secret.key')
    
    # 优先从环境变量获取
    env_secret_key = os.environ.get('SECRET_KEY')
    if env_secret_key:
        return env_secret_key
    
    # 尝试从文件读取
    if os.path.exists(secret_key_path):
        with open(secret_key_path, 'r') as f:
            key = f.read().strip()
            if key:
                return key
    
    # 生成新密钥并写入文件
    new_key = os.urandom(24).hex()
    with open(secret_key_path, 'w') as f:
        f.write(new_key)
    logger.info(f"[SECRET_KEY] 生成新密钥并保存到 {secret_key_path}")
    return new_key

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174', 'http://localhost:5175', 'http://127.0.0.1:5175'])  # 允许跨域请求（携带凭证）
app.config['SECRET_KEY'] = load_or_generate_secret_key()  # 会话加密密钥

# Session Cookie 安全配置：httpOnly 防止 XSS 窃取，SameSite 防止 CSRF
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 数据库配置 - 优先使用环境变量，默认使用 SQLite
if os.environ.get('DATABASE_URL'):
    # PostgreSQL 配置 (格式: postgresql://user:password@host:port/dbname)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # 默认 SQLite 配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'lsnuts.db')

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')  # 文件上传目录
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 上传文件最大限制：10MB

# 确保上传目录存在（不存在则自动创建）
os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 静态文件访问路由：用于访问上传的图片和附件
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # 安全校验：确保文件路径不超出 UPLOAD_FOLDER
    real_upload_folder = os.path.realpath(app.config['UPLOAD_FOLDER'])
    real_file_path = os.path.realpath(file_path)
    
    if not real_file_path.startswith(real_upload_folder + os.sep):
        return fail('非法访问', 403)
    
    if not os.path.exists(file_path):
        return fail('文件不存在', 404)
    
    return send_file(file_path)

# 注册插件
db.init_app(app)  # 初始化数据库
login_manager = LoginManager(app)  # 初始化登录管理器
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5173', 'http://127.0.0.1:5173'])  # 初始化WebSocket
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])

# Flask-Login 回调：根据用户ID从数据库加载用户对象
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 统一响应格式
def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

# 管理员权限装饰器
def admin_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return fail('请先登录', 401)
        if not current_user.is_admin:
            return fail('无权限', 403)
        return func(*args, **kwargs)
    return wrapper

# 生成唯一的6位数字账号码（保证不重复）
def generate_account_code():
    while True:
        code = ''.join(random.choices(string.digits, k=6))  # 随机生成6位数字
        if not User.query.filter_by(account_code=code).first():  # 检查是否已存在
            return code

# ========== 1. 用户认证接口 ==========
# 用户登录接口（限制每分钟最多5次尝试，防止暴力破解）
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def api_login():
    secure_info(f"[登录] 收到登录请求", request.json)
    data = request.json
    user = User.query.filter_by(username=data['username']).first()  # 根据用户名查找用户
    if not user:
        secure_warning(f"[登录] 失败 - 用户不存在: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '该用户还未注册'})
    if not verify_password(data['password'], user.password):  # 验证密码
        secure_warning(f"[登录] 失败 - 密码错误: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '密码错误'})
    login_user(user)  # 记录登录状态
    secure_info(f"[登录] 成功 - 用户: {user.username} (ID:{user.id}), 账号码: {user.account_code}")
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {
        'id': user.id, 'username': user.username, 'account_code': user.account_code, 'is_admin': user.is_admin
    }})

# 用户注册接口
@app.route('/api/register', methods=['POST'])
def api_register():
    secure_info(f"[注册] 收到注册请求", request.json)
    data = request.json
    # 检查用户名是否已被注册
    if User.query.filter_by(username=data['username']).first():
        secure_warning(f"[注册] 失败 - 用户名已存在: {data.get('username')}")
        return jsonify({'code': 400, 'msg': '用户名已存在'})
    account_code = generate_account_code()  # 生成唯一账号码
    user = User(username=data['username'], account_code=account_code, password=hash_password(data['password']))
    db.session.add(user)
    db.session.commit()
    secure_info(f"[注册] 成功 - 用户: {user.username} (ID:{user.id}), 账号码: {account_code}")
    return jsonify({'code': 200, 'msg': '注册成功', 'data': {'account_code': account_code}})

# 退出登录接口
@app.route('/api/logout')
@login_required
def api_logout():
    logout_user()  # 清除登录状态
    return jsonify({'code': 200, 'msg': '退出成功'})

# 获取当前登录用户信息接口
@app.route('/api/user/info')
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

# 头像上传接口（用户自定义上传头像）
@app.route('/api/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    if not file or file.filename == '':
        return jsonify({'code': 400, 'msg': '请选择图片'})
    
    # 检查文件类型：只允许图片格式
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'code': 400, 'msg': '仅支持png、jpg、jpeg、gif格式'})
    
    # 检查文件大小是否超过10MB限制
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:
        return jsonify({'code': 400, 'msg': '图片大小不能超过10M'})
    
    # 生成唯一文件名并保存到上传目录
    unique_name = f"avatar_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(avatar_path)
    
    # 更新数据库中用户头像字段
    current_user.avatar = f"/uploads/{unique_name}"
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '上传成功', 'data': {'avatar': current_user.avatar}})

# 修改用户名
@app.route('/api/user/username', methods=['PUT'])
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

# 修改密码
@app.route('/api/user/password', methods=['PUT'])
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

# 用户自己的帖子列表
@app.route('/api/user/posts')
@login_required
def user_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 子查询：统计每个帖子的评论数和点赞数
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

# 用户收藏列表
@app.route('/api/user/bookmarks')
@login_required
def user_bookmarks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 子查询：统计每个帖子的评论数和点赞数
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

# ========== 2. 管理员接口 ==========
# 注：管理员账号请通过后端脚本 create_admin.py 创建
# python create_admin.py [用户名] [密码]

# 管理员获取所有用户列表
@app.route('/api/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    res = [{'id': u.id, 'username': u.username, 'account_code': u.account_code, 'is_admin': u.is_admin, 'create_time': u.create_time.strftime('%Y-%m-%d %H:%M:%S')} for u in users]
    return ok(data=res)

# 管理员删除指定用户（不能删除自己）
@app.route('/api/admin/delete/<int:uid>', methods=['DELETE'])
@admin_required
def admin_delete(uid):
    if uid == current_user.id:
        return fail('不能删除自己')
    db.session.delete(User.query.get(uid))
    db.session.commit()
    return ok(msg='删除成功')

# 管理员重置用户头像为默认
@app.route('/api/admin/reset_avatar/<int:uid>', methods=['POST'])
@admin_required
def admin_reset_avatar(uid):
    user = User.query.get(uid)
    if not user:
        return fail('用户不存在')
    
    # 删除服务器上的旧头像文件（如果存在）
    if user.avatar:
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], user.avatar.replace('/uploads/', ''))
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
    
    # 将用户头像字段设为空，前端将显示默认头像
    user.avatar = None
    db.session.commit()
    
    return ok(msg='头像已重置为默认')

# 管理员修改用户信息（用户名、密码、权限）
@app.route('/api/admin/update/<int:uid>', methods=['POST'])
@admin_required
def admin_update(uid):
    if uid == current_user.id:
        return fail('不能修改自己')
    
    data = request.json
    user = User.query.get(uid)
    
    # 修改用户名，需检查是否与其他用户冲突
    if 'username' in data and data['username']:
        if User.query.filter(User.username == data['username'], User.id != uid).first():
            return fail('用户名已存在')
        user.username = data['username']
    
    # 修改密码（可为空，不填则不修改）
    if 'password' in data and data['password']:
        user.password = hash_password(data['password'])
    
    # 修改权限：提权（设为管理员）或降权（设为普通用户）
    if 'is_admin' in data:
        user.is_admin = int(data['is_admin'])
    
    db.session.commit()
    return ok(msg='修改成功')

# 管理员获取帖子列表（置顶优先，含作者用户名和评论数）
@app.route('/api/admin/posts')
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

# 管理员删除帖子（同时删除该帖子的所有评论）
@app.route('/api/admin/delete_post/<int:post_id>', methods=['DELETE'])
@admin_required
def admin_delete_post(post_id):
    Comment.query.filter(Comment.post_id == post_id).delete()  # 先删除关联评论
    db.session.delete(Post.query.get(post_id))  # 再删除帖子
    db.session.commit()
    return ok(msg='删除成功')

# 管理员置顶/取消置顶帖子
@app.route('/api/admin/toggle_pin/<int:post_id>', methods=['POST'])
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

# ========== 3. 网盘接口 ==========
# 获取当前用户的文件列表（支持分页）
@app.route('/api/drive/list')
@login_required
def drive_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = File.query.filter_by(user_id=current_user.id).order_by(File.upload_time.desc())
    total = query.count()
    files = query.offset((page - 1) * per_page).limit(per_page).all()
    data = [{'id':f.id, 'name':f.filename, 'upload_time':f.upload_time.strftime('%Y-%m-%d %H:%M:%S')} for f in files]
    return jsonify({'code':200, 'data':data, 'total': total, 'page': page, 'per_page': per_page})

# 上传文件到网盘
@app.route('/api/drive/upload', methods=['POST'])
@login_required
def drive_upload():
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'code':400, 'msg':'请选择文件'})
    filename = secure_filename(file.filename)  # 安全处理文件名
    unique_name = f"{uuid.uuid4().hex}_{filename}"  # 加UUID前缀防止重名
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
    db.session.add(File(filename=filename, file_path=unique_name, user_id=current_user.id))
    db.session.commit()
    return jsonify({'code':200, 'msg':'上传成功'})

# 下载网盘文件
@app.route('/api/drive/download/<int:file_id>')
@login_required
def drive_download(file_id):
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:  # 只能下载自己的文件
        return jsonify({'code':403, 'msg':'无权限'})
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
    return send_file(file_path, as_attachment=True, download_name=file.filename)

# 删除网盘文件（同时清除服务器物理文件和数据库记录）
@app.route('/api/drive/delete/<int:file_id>', methods=['DELETE'])
@login_required
def drive_delete(file_id):
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    # 删除服务器上的物理文件
    try:
        file_full_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
        if os.path.exists(file_full_path):
            os.remove(file_full_path)
            logger.info(f"[网盘删除] 物理文件已删除: {file_full_path}")
    except Exception as e:
        logger.warning(f"[网盘删除] 删除物理文件失败: {e}")
    db.session.delete(file)  # 删除数据库记录
    db.session.commit()
    logger.info(f"[网盘删除] 文件记录已清除 - 用户:{current_user.username} 文件:{file.filename}")
    return jsonify({'code':200, 'msg':'删除成功'})

# ========== 4. 论坛接口 ==========
# 获取论坛帖子列表（置顶帖优先，支持分页、标题搜索和标签筛选）
@app.route('/api/forum/list')
def forum_list():
    logger.info(f"[论坛列表] 收到请求 - 搜索:{request.args.get('search','')} 页码:{request.args.get('page','1')} 标签:{request.args.get('tag','')}")
    
    # 搜索和分页参数
    search = request.args.get('search', '').strip()
    tag = request.args.get('tag', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 子查询：统计每个帖子的评论数
    comment_count_subq = select(Comment.post_id, func.count(Comment.id).label('count')).group_by(Comment.post_id).subquery()
    # 子查询：统计每个帖子的点赞数
    like_count_subq = select(PostLike.post_id, func.count(PostLike.id).label('count')).group_by(PostLike.post_id).subquery()
    
    # 构建查询（使用 LEFT JOIN 避免 N+1 查询）
    query = db.session.query(
        Post, 
        User.username, 
        User.is_admin, 
        User.avatar,
        func.coalesce(comment_count_subq.c.count, 0).label('comment_count'),
        func.coalesce(like_count_subq.c.count, 0).label('like_count')
    ).join(User, Post.user_id == User.id)\
     .outerjoin(comment_count_subq, Post.id == comment_count_subq.c.post_id)\
     .outerjoin(like_count_subq, Post.id == like_count_subq.c.post_id)
    
    # 标题搜索过滤
    if search:
        query = query.filter(Post.title.contains(search))
    
    # 标签分类筛选
    if tag:
        if tag == 'other':
            query = query.filter((Post.tag == None) | (Post.tag == '') | (Post.tag == 'other'))
        else:
            query = query.filter(Post.tag == tag)
    
    # 排序：置顶优先，时间倒序
    query = query.order_by(Post.is_pinned.desc(), Post.create_time.desc())
    
    # 分页查询
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    data = []
    for post, username, is_admin, avatar, comment_count, like_count in items:
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
            'image': post.image
        })
    logger.info(f"[论坛列表] 返回 {len(data)}/{total} 条帖子数据")
    return jsonify({'code':200, 'data':data, 'total': total, 'page': page, 'per_page': per_page})

# 发布新帖（支持图片和附件上传，兼容JSON和FormData）
@app.route('/api/forum/post', methods=['POST'])
@login_required
def forum_post():
    logger.info(f"[论坛发帖] 收到请求 - 用户: {current_user.username} (ID:{current_user.id})")
    
    # 兼容两种请求体格式：JSON 和 multipart/form-data
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
    
    # 处理图片上传（仅 FormData 模式有效）
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            img_name = f"post_image_{uuid.uuid4().hex}.{ext}"
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            image_file.save(img_path)
            post.image = f"/uploads/{img_name}"
            logger.info(f"[论坛发帖] 图片已保存: {img_name}")
    
    # 处理附件上传（仅 FormData 模式有效）
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

# 获取帖子详情（含评论，支持楼中楼结构）
@app.route('/api/forum/detail/<int:post_id>')
def forum_detail(post_id):
    post_data = db.session.query(Post, User.username, User.is_admin, User.avatar).join(User, Post.user_id == User.id).filter(Post.id == post_id).first()
    if not post_data:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    post, post_username, post_is_admin, post_avatar = post_data
    
    # 点赞数
    like_count = PostLike.query.filter_by(post_id=post_id).count()
    # 当前用户是否已点赞
    user_liked = False
    user_bookmarked = False
    if current_user.is_authenticated:
        user_liked = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
        user_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    
    # 查询所有评论（含回复者信息）
    all_comments = db.session.query(Comment, User.username, User.is_admin, User.avatar).join(User, Comment.user_id == User.id).filter(Comment.post_id == post_id).order_by(Comment.create_time.asc()).all()
    
    # 构建评论树：先收集顶层评论，再把回复挂到父评论下
    comment_map = {}
    top_comments = []
    for comment, username, is_admin, avatar in all_comments:
        c = {
            'id': comment.id,
            'content': comment.content,
            'user': username,
            'is_admin': is_admin,
            'avatar': avatar,
            'parent_id': comment.parent_id,
            'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'replies': []
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
        'image': post.image, 'attachment_name': post.attachment_name, 'attachment_path': post.attachment_path
    }, 'current_user_id': current_user.id if current_user.is_authenticated else None, 'comments': top_comments}})

# 发表评论/回复（支持楼中楼，创建通知给帖子作者和被回复者）
@app.route('/api/forum/comment/<int:post_id>', methods=['POST'])
@login_required
def forum_comment(post_id):
    logger.info(f"[论坛评论] 收到请求 - 用户: {current_user.username} (ID:{current_user.id}), 帖子ID: {post_id}")
    data = request.json
    
    if not data.get('content'):
        logger.warning(f"[论坛评论] 失败 - 评论内容为空")
        return jsonify({'code':400, 'msg':'评论内容不能为空'})
    
    parent_id = data.get('parent_id')  # 楼中楼回复的父评论ID
    
    comment = Comment(content=data['content'], post_id=post_id, user_id=current_user.id, parent_id=parent_id)
    db.session.add(comment)
    
    post = Post.query.get(post_id)
    
    if parent_id:
        # 回复他人评论：通知被回复者
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
        # 回复帖子本身：通知帖子作者（作者自己评论则不通知）
        if post and post.user_id != current_user.id:
            notification = Notification(
                user_id=post.user_id,
                post_id=post_id,
                comment_id=comment.id,
                type='post_reply'
            )
            db.session.add(notification)
            logger.info(f"[通知] 创建 post_reply 通知给用户 {post.user_id}")
    
    # @提及通知：解析评论内容中的 @username 格式
    mentioned_users = re.findall(r'@(\w{2,20})', data['content'])
    if mentioned_users:
        mentioned_users = list(set(mentioned_users))  # 去重
        for username in mentioned_users:
            user = User.query.filter_by(username=username).first()
            if user and user.id != current_user.id:
                # 避免重复通知：同一个人不会被多次通知
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

# 管理员在论坛页面直接删除帖子（含评论）
@app.route('/api/forum/delete/<int:post_id>', methods=['DELETE'])
@login_required
def forum_delete(post_id):
    if current_user.is_admin != 1:
        return jsonify({'code':403, 'msg':'无权限'})
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    
    Comment.query.filter_by(post_id=post_id).delete()  # 先删除所有关联评论
    Notification.query.filter_by(post_id=post_id).delete()  # 删除关联通知
    PostLike.query.filter_by(post_id=post_id).delete()  # 删除关联点赞
    db.session.delete(post)
    db.session.commit()
    
    logger.info(f"[论坛删帖] 管理员 {current_user.username} 删除帖子 {post_id}")
    return jsonify({'code':200, 'msg':'删除成功'})

# 编辑自己的帖子（24小时内可编辑，标题和内容均可修改）
@app.route('/api/forum/post/<int:post_id>', methods=['PUT'])
@login_required
def forum_edit(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code':400, 'msg':'帖子不存在'})
    if post.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'只能编辑自己的帖子'})
    
    # 24小时限制
    from datetime import timedelta
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

# 用户删除自己的帖子
@app.route('/api/forum/post/<int:post_id>', methods=['DELETE'])
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

# 帖子点赞/取消点赞
@app.route('/api/forum/like/<int:post_id>', methods=['POST'])
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

# 收藏/取消收藏帖子
@app.route('/api/forum/bookmark/<int:post_id>', methods=['POST'])
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

# 下载论坛帖子附件
@app.route('/api/forum/attachment/<int:post_id>')
@login_required
def forum_attachment_download(post_id):
    post = Post.query.get(post_id)
    if not post or not post.attachment_path:
        return jsonify({'code':400, 'msg':'附件不存在'})
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(post.attachment_path))
    if not os.path.exists(file_path):
        return jsonify({'code':400, 'msg':'附件文件不存在'})
    return send_file(file_path, as_attachment=True, download_name=post.attachment_name or 'attachment')

# ========== 4.5 通知接口 ==========
# 获取当前用户的未读通知数量
@app.route('/api/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=0).count()
    return jsonify({'code': 200, 'data': {'count': count}})

# 获取当前用户的通知列表（含上下文信息，帖子被删除时仍显示）
@app.route('/api/notifications')
@login_required
def notification_list():
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

# 标记所有通知为已读
@app.route('/api/notifications/read', methods=['POST'])
@login_required
def notification_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=0).update({'is_read': 1})
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已全部标记为已读'})

# 删除单条通知
@app.route('/api/notifications/<int:notif_id>', methods=['DELETE'])
@login_required
def notification_delete(notif_id):
    n = Notification.query.get(notif_id)
    if not n or n.user_id != current_user.id:
        return jsonify({'code':404, 'msg':'通知不存在'})
    db.session.delete(n)
    db.session.commit()
    return jsonify({'code':200, 'msg':'已删除'})

# ========== 5. 实时聊天（SocketIO） ==========
# 用户加入聊天房间
@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    logger.info(f"[SocketIO-join] 用户加入 - user_id: {user_id}, sid: {request.sid}")
    if user_id:
        socketio.server.enter_room(request.sid, str(user_id))
        logger.info(f"[SocketIO-join] 用户 {user_id} 已加入房间")

# 发送聊天消息（支持私聊和群聊）
@socketio.on('send_message')
def handle_send_msg(data):
    logger.info(f"[SocketIO-send_message] 收到消息 - data: {data}")
    
    if not current_user.is_authenticated:
        logger.warning(f"[SocketIO-send_message] 失败 - 用户未认证")
        return
    
    logger.info(f"[SocketIO-send_message] 发送者: {current_user.username} (ID:{current_user.id})")
    
    receiver_id = data.get('receiver_id')
    if receiver_id:
        # 私聊模式：发送给指定用户
        receiver = User.query.get(receiver_id)
        logger.info(f"[SocketIO-send_message] 私聊模式 - 接收者ID: {receiver_id}, 接收者: {receiver.username if receiver else '不存在'}")
        
        if receiver:
            msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=data['content'])
            db.session.add(msg)
            db.session.commit()
            logger.info(f"[SocketIO-send_message] 消息已存储 - msg_id: {msg.id}")
            
            msg_data = {
                'sender': current_user.username,
                'sender_id': current_user.id,
                'receiver_id': receiver_id,
                'content': data['content'],
                'send_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            emit('receive_message', msg_data, room=str(receiver_id))  # 发送给接收方
            emit('receive_message', msg_data, room=str(current_user.id))  # 也发送给自己
            logger.info(f"[SocketIO-send_message] 消息已发送")
        else:
            logger.warning(f"[SocketIO-send_message] 失败 - 接收者不存在 receiver_id: {receiver_id}")
    else:
        # 群聊模式：广播给所有在线用户
        logger.info(f"[SocketIO-send_message] 群聊模式 - 广播消息")
        emit('receive_message', {
            'sender': current_user.username,
            'content': data['content'],
            'send_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, broadcast=True)

# 获取与指定用户的聊天记录
@app.route('/api/chat/history/<int:other_id>')
@login_required
def chat_history(other_id):
    logger.info(f"[聊天记录] 用户 {current_user.id} 请求与用户 {other_id} 的聊天记录")
    
    # 获取分页参数
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # 构建查询
    query = db.session.query(Message, User.username).join(User, Message.sender_id == User.id).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.send_time.asc())
    
    # 获取总数
    total = query.count()
    
    # 分页查询
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

# 搜索用户（支持按ID、账号码、用户名模糊搜索）
@app.route('/api/user/search')
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

# 获取所有用户列表（排除自己，供前端展示）
@app.route('/api/user/list')
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

# 启动应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 自动创建数据表
        # 自动迁移：为 posts 表添加新字段
        for col_name, col_type in [('image', 'VARCHAR(255)'), ('attachment_name', 'VARCHAR(255)'), ('attachment_path', 'VARCHAR(255)'), ('is_pinned', 'INTEGER DEFAULT 0'), ('tag', 'VARCHAR(20)'), ('edit_count', 'INTEGER DEFAULT 0'), ('last_edit_time', 'DATETIME')]:
            try:
                db.engine.execute(f'ALTER TABLE posts ADD COLUMN {col_name} {col_type}')
                logger.info(f"[迁移] posts 表 {col_name} 字段添加成功")
            except Exception:
                pass  # 字段已存在则忽略
        # 自动迁移：为 comments 表添加 parent_id 字段
        try:
            db.engine.execute('ALTER TABLE comments ADD COLUMN parent_id INTEGER')
            logger.info(f"[迁移] comments 表 parent_id 字段添加成功")
        except Exception:
            pass
        # 自动迁移：为 notifications 表添加 type 字段
        try:
            db.engine.execute("ALTER TABLE notifications ADD COLUMN type VARCHAR(20) DEFAULT 'comment_reply'")
            logger.info(f"[迁移] notifications 表 type 字段添加成功")
        except Exception:
            pass
        # 自动迁移：创建 post_likes 表
        try:
            db.engine.execute("""CREATE TABLE IF NOT EXISTS post_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_id INTEGER,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, post_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )""")
            logger.info(f"[迁移] post_likes 表创建成功")
        except Exception:
            pass
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)