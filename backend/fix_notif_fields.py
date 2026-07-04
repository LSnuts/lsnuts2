import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db

with app.app_context():
    try:
        db.engine.execute('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS sender_id INTEGER')
        print("Added sender_id column")
    except Exception as e:
        print(f"sender_id already exists: {e}")
    
    try:
        db.engine.execute('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS message_id INTEGER')
        print("Added message_id column")
    except Exception as e:
        print(f"message_id already exists: {e}")
    
    try:
        db.engine.execute('ALTER TABLE notifications ADD CONSTRAINT IF NOT EXISTS fk_notif_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE')
        print("Added fk_notif_sender constraint")
    except Exception as e:
        print(f"fk_notif_sender already exists: {e}")
    
    try:
        db.engine.execute('ALTER TABLE notifications ADD CONSTRAINT IF NOT EXISTS fk_notif_message FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE')
        print("Added fk_notif_message constraint")
    except Exception as e:
        print(f"fk_notif_message already exists: {e}")
    
    print("\nDatabase fix completed!")