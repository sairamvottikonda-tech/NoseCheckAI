"""
WSGI entry point when Render Root Directory is set to 'src'.
Use: gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:application
"""
from app import app

application = app
