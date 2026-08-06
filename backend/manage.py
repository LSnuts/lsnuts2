import sys

from flask_migrate import upgrade, init, migrate as alembic_migrate

from app import app

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]

        with app.app_context():
            from flask import g
            g.x_arg = []
            app.extensions['migrate'].configure_args.setdefault('x_arg', [])
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
