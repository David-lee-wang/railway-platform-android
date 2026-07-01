# -*- coding: utf-8 -*-
"""
Railway Platform - Android Entry Point
Called by MainActivity.java via Chaquopy to start Flask server
"""
import os
import sys
import threading

# Set up paths for Android
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('ANDROID_DATA_DIR', '/data/user/0/com.railway.platform')
DB_PATH = os.path.join(DATA_DIR, 'railway_platform.db')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def start_server(port=5001):
    """Start the Flask server on the given port. Returns 'OK' on success."""
    sys.path.insert(0, BASE_DIR)

    # Import after path setup
    from app import create_app
    from extensions import db
    from models import User, UserRole

    app = create_app()

    # Configure database for Android
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'

    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            from datetime import datetime
            admin = User(
                username='admin',
                real_name='系统管理员',
                password_hash=generate_password_hash('admin123'),
                role=UserRole.super_admin,
                created_at=datetime.now()
            )
            db.session.add(admin)
            db.session.commit()

    # Run in background thread so it doesn't block Java
    def run_app():
        app.run(host='127.0.0.1', port=port, debug=False, threaded=True)

    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()

    # Wait briefly for server to start
    import time; time.sleep(1)
    return "OK"
