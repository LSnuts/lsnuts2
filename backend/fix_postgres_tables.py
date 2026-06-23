#!/usr/bin/env python3
"""
修复 PostgreSQL 表结构 - 将 id 列改为 SERIAL 自增类型
"""

import psycopg2

# PostgreSQL 数据库配置
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_DB_NAME = 'garden1'
PG_USER = 'lsnuts'
PG_PASSWORD = '123456'

# 需要修复的表
TABLES = ['users', 'files', 'messages', 'posts', 'comments', 'notifications', 'post_likes', 'bookmarks']

def fix_tables():
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB_NAME,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cursor = conn.cursor()
    
    print("开始修复 PostgreSQL 表结构...")
    
    for table in TABLES:
        try:
            # 检查当前 id 列的最大值
            cursor.execute(f"SELECT MAX(id) FROM {table};")
            max_id = cursor.fetchone()[0]
            if max_id is None:
                max_id = 0
            
            # 创建新的序列
            seq_name = f"{table}_id_seq"
            cursor.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq_name};")
            cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_id + 1};")
            
            # 将 id 列设置为使用序列
            cursor.execute(f"ALTER TABLE {table} ALTER COLUMN id SET DEFAULT nextval('{seq_name}');")
            cursor.execute(f"ALTER SEQUENCE {seq_name} OWNED BY {table}.id;")
            
            print(f"OK 修复表 {table} - 当前最大ID: {max_id}")
        except Exception as e:
            print(f"ERROR 修复表 {table} 失败: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n修复完成！")

if __name__ == '__main__':
    fix_tables()