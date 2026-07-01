# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('ANDROID_DATA_DIR', BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, 'railway_platform.db')
UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')

class Config:
    SECRET_KEY = 'railway-platform-mobile-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
