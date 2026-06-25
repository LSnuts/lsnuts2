from flask import Flask
from flask_migrate import Migrate

from app import app, db, migrate

if __name__ == '__main__':
    from flask_migrate import upgrade, init, migrate as alembic_migrate
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        with app.app_context():
            if command == 'init':
                init()
                print("Migration directory initialized")
            elif command == 'migrate':
                message = sys.argv[2] if len(sys.argv) > 2 else 'auto migration'
                alembic_migrate(message=message)
                print(f"Migration created: {message}")
            elif command == 'upgrade':
                upgrade()
                print("Database upgraded")
            else:
                print(f"Unknown command: {command}")
    else:
        print("Usage: python manage.py [init|migrate|upgrade]")
