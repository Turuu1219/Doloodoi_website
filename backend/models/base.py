"""
backend/models/base.py
SQLAlchemy db instance — imported by all models and app factory.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
