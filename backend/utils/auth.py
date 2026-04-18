"""
backend/utils/auth.py
Authentication helpers: bcrypt, session tokens, decorators.
"""
import hashlib, uuid, logging
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
from flask import request, jsonify

from backend.config import Config

logger = logging.getLogger(__name__)


# ── Password ──────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ── Token ─────────────────────────────────────────────────────
def generate_token() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ── Session (uses ORM) ────────────────────────────────────────
def create_session(admin_id: int, ip: str, ua: str) -> str:
    from backend.models.models import AdminSession
    from backend.models.base   import db
    token   = generate_token()
    t_hash  = hash_token(token)
    expires = datetime.utcnow() + timedelta(hours=Config.SESSION_HOURS)
    sess    = AdminSession(admin_id=admin_id, token_hash=t_hash,
                           ip_address=ip, user_agent=(ua or "")[:300],
                           expires_at=expires)
    db.session.add(sess)
    db.session.commit()
    return token


def validate_session(token: str):
    """Return Admin ORM object or None."""
    if not token:
        return None
    from backend.models.models import Admin, AdminSession
    t_hash = hash_token(token)
    sess   = (AdminSession.query
              .filter_by(token_hash=t_hash)
              .filter(AdminSession.expires_at > datetime.utcnow())
              .first())
    if not sess:
        return None
    admin = Admin.query.filter_by(id=sess.admin_id, is_active=True).first()
    return admin


def destroy_session(token: str):
    if not token:
        return
    from backend.models.models import AdminSession
    from backend.models.base   import db
    t_hash = hash_token(token)
    AdminSession.query.filter_by(token_hash=t_hash).delete()
    db.session.commit()


# ── Decorators ────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("admin_token") or request.headers.get("X-Admin-Token")
        admin = validate_session(token)
        if not admin:
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        request.admin = admin
        return f(*args, **kwargs)
    return decorated


def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("admin_token") or request.headers.get("X-Admin-Token")
        admin = validate_session(token)
        if not admin:
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        if admin.role != "superadmin":
            return jsonify({"success": False, "error": "Forbidden — superadmin only"}), 403
        request.admin = admin
        return f(*args, **kwargs)
    return decorated
