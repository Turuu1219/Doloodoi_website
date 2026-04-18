"""
backend/utils/helpers.py
Shared utilities: file upload, JSON responses, audit logging, pagination.
"""
import os, uuid, logging
from flask import jsonify, request
from backend.config import Config

logger = logging.getLogger(__name__)


# ── Standard JSON responses ───────────────────────────────────
def ok(data=None, message="success", status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status

def err(message="An error occurred", status=400):
    return jsonify({"success": False, "error": message}), status

def paginate(query, page: int, per_page: int):
    """Paginate a SQLAlchemy query. Returns dict with items + meta."""
    total  = query.count()
    items  = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items":    [i.to_dict() for i in items],
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    max(1, (total + per_page - 1) // per_page),
    }


# ── File uploads ──────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_upload(file_obj, subfolder: str = "") -> str | None:
    if not file_obj or not file_obj.filename:
        return None
    if not allowed_file(file_obj.filename):
        logger.warning("Rejected upload: %s", file_obj.filename)
        return None
    ext    = file_obj.filename.rsplit(".", 1)[1].lower()
    fname  = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    file_obj.save(os.path.join(folder, fname))
    parts = ["/static", "uploads"]
    if subfolder:
        parts.append(subfolder)
    parts.append(fname)
    return "/".join(parts)


# ── Audit log ─────────────────────────────────────────────────
def log_audit(admin_id: int, table: str, action: str, record_id=None, note=None):
    try:
        from backend.models.models import AuditLog
        from backend.models.base   import db
        entry = AuditLog(admin_id=admin_id, table_name=table, action=action,
                         record_id=record_id, note=note, ip_address=request.remote_addr)
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        logger.error("audit_log failed: %s", e)


# ── Input validation ──────────────────────────────────────────
def require_fields(data: dict, *fields):
    """Return list of missing required fields."""
    return [f for f in fields if not data.get(f)]
