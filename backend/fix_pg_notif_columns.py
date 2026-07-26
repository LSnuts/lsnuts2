"""修复 PostgreSQL notifications 表缺少的列"""
import psycopg2

PG_HOST = 'localhost'
PG_PORT = '5432'
PG_DB_NAME = 'garden1'
PG_USER = 'lsnuts'
PG_PASSWORD = '123456'

conn = psycopg2.connect(
    host=PG_HOST, port=PG_PORT, dbname=PG_DB_NAME,
    user=PG_USER, password=PG_PASSWORD
)
cur = conn.cursor()

# 检查现有列
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='notifications'")
cols = [r[0] for r in cur.fetchall()]
print('现有列:', cols)

# 添加 sender_id
if 'sender_id' not in cols:
    cur.execute('ALTER TABLE notifications ADD COLUMN sender_id INTEGER')
    try:
        cur.execute('ALTER TABLE notifications ADD CONSTRAINT fk_notif_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE')
    except Exception as e:
        print(f'外键约束已存在或添加失败: {e}')
    print('OK 已添加 sender_id')
else:
    print('sender_id 已存在')

# 添加 message_id
if 'message_id' not in cols:
    cur.execute('ALTER TABLE notifications ADD COLUMN message_id INTEGER')
    try:
        cur.execute('ALTER TABLE notifications ADD CONSTRAINT fk_notif_message FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE')
    except Exception as e:
        print(f'外键约束已存在或添加失败: {e}')
    print('OK 已添加 message_id')
else:
    print('message_id 已存在')

conn.commit()
cur.close()
conn.close()
print('修复完成!')
