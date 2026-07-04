from app import app
from models import db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('notifications')]
    
    print("当前notifications表的字段:", columns)
    
    if 'sender_id' not in columns:
        print("添加sender_id字段...")
        db.engine.execute('ALTER TABLE notifications ADD COLUMN sender_id INTEGER')
        db.engine.execute('ALTER TABLE notifications ADD CONSTRAINT fk_sender_id FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE')
    
    if 'message_id' not in columns:
        print("添加message_id字段...")
        db.engine.execute('ALTER TABLE notifications ADD COLUMN message_id INTEGER')
        db.engine.execute('ALTER TABLE notifications ADD CONSTRAINT fk_message_id FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE')
    
    print("修复完成!")