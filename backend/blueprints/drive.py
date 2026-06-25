import os
import uuid
import logging
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user

from models import db, File
from werkzeug.utils import secure_filename

drive_bp = Blueprint('drive', __name__)
logger = logging.getLogger(__name__)

def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})

def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code

@drive_bp.route('/api/drive/list')
@login_required
def drive_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', '')
    
    query = File.query.filter_by(user_id=current_user.id)
    if category:
        query = query.filter_by(category=category)
    query = query.order_by(File.upload_time.desc())
    
    total = query.count()
    files = query.offset((page - 1) * per_page).limit(per_page).all()
    data = [{
        'id':f.id, 
        'name':f.filename, 
        'upload_time':f.upload_time.strftime('%Y-%m-%d %H:%M:%S'), 
        'file_path': f.file_path,
        'category': f.category,
        'share_token': f.share_token,
        'share_expire': f.share_expire.strftime('%Y-%m-%d %H:%M:%S') if f.share_expire else None
    } for f in files]
    return jsonify({'code':200, 'data':data, 'total': total, 'page': page, 'per_page': per_page})

@drive_bp.route('/api/drive/upload', methods=['POST'])
@login_required
def drive_upload():
    from app import app
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'code':400, 'msg':'请选择文件'})
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
    
    category = request.form.get('category', '默认')
    db.session.add(File(filename=filename, file_path=unique_name, user_id=current_user.id, category=category))
    db.session.commit()
    return jsonify({'code':200, 'msg':'上传成功'})

@drive_bp.route('/api/drive/download/<int:file_id>')
@login_required
def drive_download(file_id):
    from app import app
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
    return send_file(file_path, as_attachment=True, download_name=file.filename)

@drive_bp.route('/api/drive/delete/<int:file_id>', methods=['DELETE'])
@login_required
def drive_delete(file_id):
    from app import app
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    try:
        file_full_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
        if os.path.exists(file_full_path):
            os.remove(file_full_path)
            logger.info(f"[网盘删除] 物理文件已删除: {file_full_path}")
    except Exception as e:
        logger.warning(f"[网盘删除] 删除物理文件失败: {e}")
    db.session.delete(file)
    db.session.commit()
    logger.info(f"[网盘删除] 文件记录已清除 - 用户:{current_user.username} 文件:{file.filename}")
    return jsonify({'code':200, 'msg':'删除成功'})

@drive_bp.route('/api/drive/categories')
@login_required
def drive_categories():
    from sqlalchemy import func
    
    categories = db.session.query(File.category, func.count(File.id)).filter_by(user_id=current_user.id).group_by(File.category).all()
    
    all_categories = []
    for cat, count in categories:
        all_categories.append({'name': cat, 'count': count})
    
    return jsonify({'code': 200, 'data': all_categories})

@drive_bp.route('/api/drive/update-category/<int:file_id>', methods=['POST'])
@login_required
def drive_update_category(file_id):
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    
    data = request.json
    new_category = data.get('category', '默认')
    file.category = new_category
    db.session.commit()
    
    return jsonify({'code':200, 'msg':'分类更新成功'})

@drive_bp.route('/api/drive/share/<int:file_id>', methods=['POST'])
@login_required
def drive_share(file_id):
    from datetime import timedelta
    
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    
    days = request.json.get('days', 7)
    file.share_token = uuid.uuid4().hex
    file.share_expire = datetime.now(timezone.utc) + timedelta(days=days)
    db.session.commit()
    
    share_url = f"{request.host_url}drive/share/{file.share_token}"
    return jsonify({'code':200, 'msg':'分享成功', 'data': {'url': share_url, 'expire': file.share_expire.strftime('%Y-%m-%d %H:%M:%S')}})

@drive_bp.route('/api/drive/unshare/<int:file_id>', methods=['POST'])
@login_required
def drive_unshare(file_id):
    file = File.query.get(file_id)
    if not file or file.user_id != current_user.id:
        return jsonify({'code':403, 'msg':'无权限'})
    
    file.share_token = None
    file.share_expire = None
    db.session.commit()
    
    return jsonify({'code':200, 'msg':'已取消分享'})

@drive_bp.route('/api/drive/share/download/<string:token>')
def drive_share_download(token):
    from app import app
    
    file = File.query.filter_by(share_token=token).first()
    if not file:
        return jsonify({'code':404, 'msg':'分享链接不存在'})
    
    if file.share_expire and file.share_expire < datetime.now(timezone.utc):
        return jsonify({'code':410, 'msg':'分享链接已过期'})
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
    return send_file(file_path, as_attachment=True, download_name=file.filename)

@drive_bp.route('/api/drive/share/check/<string:token>')
def drive_share_check(token):
    file = File.query.filter_by(share_token=token).first()
    if not file:
        return jsonify({'code':404, 'msg':'分享链接不存在'})
    
    if file.share_expire and file.share_expire < datetime.now(timezone.utc):
        return jsonify({'code':410, 'msg':'分享链接已过期'})
    
    return jsonify({'code':200, 'data': {
        'filename': file.filename,
        'expire': file.share_expire.strftime('%Y-%m-%d %H:%M:%S') if file.share_expire else '永久'
    }})

@drive_bp.route('/api/drive/stats')
@login_required
def drive_stats():
    from app import app
    total_files = File.query.filter_by(user_id=current_user.id).count()
    total_size = 0
    files = File.query.filter_by(user_id=current_user.id).all()
    for f in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.file_path)
        if os.path.exists(file_path):
            total_size += os.path.getsize(file_path)
    
    return jsonify({'code': 200, 'data': {
        'total_files': total_files,
        'used_bytes': total_size,
        'used_human': format_size(total_size),
        'total_bytes': 10 * 1024 * 1024 * 1024,
        'total_human': '10GB'
    }})

def format_size(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"
