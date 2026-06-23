#!/usr/bin/env python3
"""
数据库迁移脚本：从 SQLite 迁移到 PostgreSQL

使用方法：
1. 确保已安装 PostgreSQL 和 psycopg2-binary
2. 创建 PostgreSQL 数据库和用户
3. 修改下面的配置参数
4. 运行脚本: python migrate_to_postgres.py
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2 import sql

# ========== 配置参数 ==========
# SQLite 源数据库路径
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'lsnuts.db')

# PostgreSQL 目标数据库配置
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_DB_NAME = 'garden1'
PG_USER = 'lsnuts'
PG_PASSWORD = '123456'

def get_sqlite_tables(conn):
    """获取 SQLite 数据库中的所有表"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def get_table_schema_sqlite(conn, table_name):
    """获取 SQLite 表的创建语句和列信息"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    cursor.close()
    return columns

def sqlite_to_postgres_type(sqlite_type):
    """SQLite 类型映射到 PostgreSQL 类型"""
    sqlite_type = sqlite_type.lower()
    if 'integer' in sqlite_type:
        return 'INTEGER'
    elif 'text' in sqlite_type:
        return 'TEXT'
    elif 'varchar' in sqlite_type:
        return 'VARCHAR'
    elif 'datetime' in sqlite_type:
        return 'TIMESTAMP'
    elif 'boolean' in sqlite_type:
        return 'BOOLEAN'
    else:
        return 'TEXT'

def create_postgres_table(pg_conn, table_name, sqlite_columns):
    """根据 SQLite 列信息创建 PostgreSQL 表"""
    cursor = pg_conn.cursor()
    
    # 构建 CREATE TABLE 语句
    columns_def = []
    primary_keys = []
    
    for col in sqlite_columns:
        col_name = col[1]
        col_type = sqlite_to_postgres_type(col[2])
        not_null = 'NOT NULL' if col[3] == 1 else ''
        default_val = f"DEFAULT {col[4]}" if col[4] is not None else ''
        
        # 处理主键
        if col[5] == 1:
            primary_keys.append(col_name)
            columns_def.append(f"{col_name} {col_type} PRIMARY KEY")
        else:
            parts = [col_name, col_type]
            if not_null:
                parts.append(not_null)
            if default_val:
                parts.append(default_val)
            columns_def.append(' '.join(parts))
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_def)})"
    
    try:
        cursor.execute(create_sql)
        pg_conn.commit()
        print(f"OK 创建表 {table_name}")
    except Exception as e:
        print(f"ERROR 创建表 {table_name} 失败: {e}")
        pg_conn.rollback()
    
    cursor.close()

def copy_data(sqlite_conn, pg_conn, table_name):
    """从 SQLite 复制数据到 PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # 获取列名
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    column_names = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    
    # 获取所有数据
    sqlite_cursor.execute(f"SELECT {column_names} FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  表 {table_name} 没有数据")
        return
    
    # 插入数据
    try:
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        pg_cursor.executemany(insert_sql, rows)
        pg_conn.commit()
        print(f"  OK 复制了 {len(rows)} 条数据")
    except Exception as e:
        print(f"  ERROR 复制数据失败: {e}")
        pg_conn.rollback()
    
    sqlite_cursor.close()
    pg_cursor.close()

def main():
    print("=" * 60)
    print("SQLite 到 PostgreSQL 数据库迁移脚本")
    print("=" * 60)
    
    # 1. 连接 SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        print(f"OK 成功连接 SQLite 数据库: {SQLITE_DB_PATH}")
    except Exception as e:
        print(f"ERROR 连接 SQLite 失败: {e}")
        sys.exit(1)
    
    # 2. 连接 PostgreSQL
    try:
        pg_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB_NAME,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print(f"OK 成功连接 PostgreSQL 数据库: {PG_HOST}:{PG_PORT}/{PG_DB_NAME}")
    except Exception as e:
        print(f"ERROR 连接 PostgreSQL 失败: {e}")
        print("\n请确保：")
        print("1. PostgreSQL 服务已启动")
        print("2. 数据库 lsnuts 已创建")
        print("3. 用户 lsnuts_user 已创建并具有权限")
        sqlite_conn.close()
        sys.exit(1)
    
    # 3. 获取所有表
    tables = get_sqlite_tables(sqlite_conn)
    print(f"\n发现 {len(tables)} 个表: {', '.join(tables)}")
    
    # 4. 创建表并复制数据
    print("\n开始迁移数据...")
    for table in tables:
        print(f"\n处理表: {table}")
        columns = get_table_schema_sqlite(sqlite_conn, table)
        create_postgres_table(pg_conn, table, columns)
        copy_data(sqlite_conn, pg_conn, table)
    
    # 5. 关闭连接
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("请更新 backend/app.py 中的数据库连接配置")
    print("=" * 60)

if __name__ == '__main__':
    main()
