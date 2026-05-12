import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'educare-secret-key-2026'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'educare_db'