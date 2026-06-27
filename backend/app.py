import os
import uuid
import functools
import logging
from datetime import datetime, timezone

# 加载环境变量配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from models import db, User, File, Message, Post, Comment, Notification, PostLike, Bookmark
from utils import hash_password, verify_password
from utils.secure_logger import info as secure_info, warning as secure_warning
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_or_generate_secret_key():
    secret_key_path = os.path.join(os.path.dirname(__file__), 'secret.key')
    
    env_secret_key = os.environ.get('SECRET_KEY')
    if env_secret_key:
        return env_secret_key
    
    if os.path.exists(secret_key_path):
        with open(secret_key_path, 'r') as f:
            key = f.read().strip()
            if key:
                return key
    
    new_key = os.urandom(24).hex()
    with open(secret_key_path, 'w') as f:
        f.write(new_key)
    logger.info(f"[SECRET_KEY] 生成新密钥并保存到 {secret_key_path}")
    return new_key

app = Flask(__name__)

allowed_origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
    'http://localhost:5175',
    'http://127.0.0.1:5175',
]
frontend_url = os.environ.get('FRONTEND_URL')
if frontend_url:
    allowed_origins.append(frontend_url)

CORS(app, supports_credentials=True, origins=allowed_origins)
app.config['SECRET_KEY'] = load_or_generate_secret_key()

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'lsnuts.db')

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.request_loader
def load_user_from_request(request):
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'code': 401, 'msg': '请先登录'}), 401
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])
migrate = Migrate(app, db)

from blueprints.auth import auth_bp
from blueprints.forum import forum_bp
from blueprints.drive import drive_bp
from blueprints.admin import admin_bp
from blueprints.chat import chat_bp

app.register_blueprint(auth_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(drive_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chat_bp)



@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    real_upload_folder = os.path.realpath(app.config['UPLOAD_FOLDER'])
    real_file_path = os.path.realpath(file_path)
    
    if not real_file_path.startswith(real_upload_folder + os.sep):
        return jsonify({'code': 403, 'msg': '非法访问'}), 403
    
    if not os.path.exists(file_path):
        return jsonify({'code': 404, 'msg': '文件不存在'}), 404
    
    return send_file(file_path)

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    logger.info(f"[SocketIO-join] 用户加入 - user_id: {user_id}, sid: {request.sid}")
    if user_id:
        socketio.server.enter_room(request.sid, str(user_id))
        logger.info(f"[SocketIO-join] 用户 {user_id} 已加入房间")

@socketio.on('send_message')
def handle_send_msg(data):
    logger.info(f"[SocketIO-send_message] 收到消息 - data: {data}")
    
    if not current_user.is_authenticated:
        logger.warning(f"[SocketIO-send_message] 失败 - 用户未认证")
        return
    
    logger.info(f"[SocketIO-send_message] 发送者: {current_user.username} (ID:{current_user.id})")
    
    receiver_id = data.get('receiver_id')
    if receiver_id:
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
            emit('receive_message', msg_data, room=str(receiver_id))
            emit('receive_message', msg_data, room=str(current_user.id))
            logger.info(f"[SocketIO-send_message] 消息已发送")
        else:
            logger.warning(f"[SocketIO-send_message] 失败 - 接收者不存在 receiver_id: {receiver_id}")
    else:
        logger.info(f"[SocketIO-send_message] 群聊模式 - 广播消息")
        emit('receive_message', {
            'sender': current_user.username,
            'content': data['content'],
            'send_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
