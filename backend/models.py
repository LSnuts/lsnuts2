from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

# 初始化数据库对象
db = SQLAlchemy()

# 用户表 - 存储所有用户信息
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名，唯一且不能为空
    account_code = db.Column(db.String(6), unique=True, nullable=False)  # 六位数字账号码，用于搜索用户
    password = db.Column(db.String(100), nullable=False)  # 密码（加密存储）
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 注册时间
    is_admin = db.Column(db.Integer, default=0)  # 权限标识：0=普通用户，1=管理员
    avatar = db.Column(db.String(255))  # 头像文件路径（为空则使用默认头像）

# 网盘文件表 - 存储用户上传的文件信息
class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)  # 文件ID，主键
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_path = db.Column(db.String(255), nullable=False)  # 服务器上的存储路径
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 上传者ID，关联用户表
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 上传时间
    
    user = db.relationship('User', backref=db.backref('files', lazy=True, cascade='all, delete-orphan'))  # 关联用户对象

# 聊天消息表 - 存储用户间的私聊消息
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)  # 消息ID，主键
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 发送者ID
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 接收者ID
    content = db.Column(db.Text, nullable=False)  # 消息内容
    send_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 发送时间
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True, cascade='all, delete-orphan'))  # 发送者关联
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy=True, cascade='all, delete-orphan'))  # 接收者关联

# 论坛帖子表 - 存储用户发布的帖子
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)  # 帖子ID，主键
    title = db.Column(db.String(100), nullable=False)  # 帖子标题
    content = db.Column(db.Text, nullable=False)  # 帖子内容
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 发帖者ID
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 发布时间
    is_pinned = db.Column(db.Integer, default=0)  # 是否置顶：0=不置顶，1=置顶
    tag = db.Column(db.String(20))  # 帖子分类标签：tech/help/chat/null(其他)
    edit_count = db.Column(db.Integer, default=0)  # 编辑次数
    last_edit_time = db.Column(db.DateTime)  # 最后编辑时间
    image = db.Column(db.String(255))  # 帖子配图存储路径
    attachment_name = db.Column(db.String(255))  # 附件原始文件名
    attachment_path = db.Column(db.String(255))  # 附件存储路径
    
    user = db.relationship('User', backref=db.backref('posts', lazy=True, cascade='all, delete-orphan'))  # 发帖者关联
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')  # 帖子的评论列表
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')  # 帖子的点赞列表

# 论坛评论表 - 存储用户对帖子的回复（支持楼中楼）
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)  # 评论ID，主键
    content = db.Column(db.Text, nullable=False)  # 评论内容
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))  # 所属帖子ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 评论者ID
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)  # 父评论ID（楼中楼回复）
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 评论时间
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))  # 评论者关联
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True, cascade='all, delete-orphan')  # 子回复列表

# 通知表 - 存储用户收到的评论回复通知
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 接收通知的用户
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))  # 相关帖子ID
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'))  # 相关评论ID
    type = db.Column(db.String(20), default='comment_reply')  # post_reply / comment_reply / mention
    is_read = db.Column(db.Integer, default=0)  # 是否已读：0=未读，1=已读
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# 帖子点赞表 - 记录用户对帖子的点赞（每个用户每个帖子仅一条）
class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),)

# 帖子收藏表
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True, cascade='all, delete-orphan'))
    post = db.relationship('Post')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_bookmark'),)