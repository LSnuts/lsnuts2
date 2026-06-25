#!/usr/bin/env python3
"""
CLI 脚本：创建/重置管理员账号
用法：python create_admin.py [username] [password]
默认：python create_admin.py admin admin123
"""
import os
import sys
import uuid

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入 Flask 应用上下文
from app import app, db
from models import User
from utils import hash_password

def generate_account_code():
    import random, string
    while True:
        code = ''.join(random.choices(string.digits, k=6))
        if not User.query.filter_by(account_code=code).first():
            return code

def create_admin(username='admin', password='admin123', force=False):
    with app.app_context():
        # 先确保表存在
        db.create_all()
        
        # 检查是否已有同名用户
        existing = User.query.filter_by(username=username).first()
        if existing:
            if force:
                existing.password = hash_password(password)
                existing.is_admin = 1
                db.session.commit()
                print(f"[OK] 用户 '{username}' 已重置密码并设为管理员")
            else:
                print(f"[INFO] 用户 '{username}' 已存在，跳过创建（使用 -f 参数强制重置）")
            return

        # 创建新管理员
        admin = User(
            username=username,
            account_code=generate_account_code(),
            password=hash_password(password),
            is_admin=1
        )
        db.session.add(admin)
        db.session.commit()
        print(f"[OK] 管理员创建成功！")
        print(f"     用户名: {username}")
        print(f"     密码: {password}")
        print(f"     账号码: {admin.account_code}")

if __name__ == '__main__':
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
    force = '-f' in sys.argv or '--force' in sys.argv
    create_admin(username, password, force)
