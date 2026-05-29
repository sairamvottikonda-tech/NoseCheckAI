"""
WSGI entry point for production deployment (Render, Gunicorn, etc.)
Use when Render Root Directory is EMPTY (repo root).
"""
from src.app import app

application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
