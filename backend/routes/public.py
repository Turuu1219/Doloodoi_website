"""
backend/routes/public.py
Public Blueprint — /api/*
No authentication required.
"""
from datetime import date
from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc

from backend.models.base    import db
from backend.models.models  import (SchoolInfo, SchoolPhoto, Director, Teacher,
                                     Class, News, Achievement, Announcement,
                                     GalleryAlbum, FAQ, Graduate)
from backend.utils.helpers  import ok, err, paginate, save_upload

public_bp = Blueprint("public", __name__)


# ── School ────────────────────────────────────────────────────
@public_bp.get("/api/school")
def get_school():
    """
    ---
    summary: Get school information
    tags: [Public]
    responses:
      200:
        description: School info object
    """
    row = SchoolInfo.query.first()
    return jsonify(row.to_dict() if row else {})


@public_bp.get("/api/school-photos")
def get_school_photos():
    photos = SchoolPhoto.query.order_by(SchoolPhoto.sort_order).all()
    return jsonify([p.to_dict() for p in photos])


# ── Director ──────────────────────────────────────────────────
@public_bp.get("/api/director")
def get_director():
    row = Director.query.first()
    return jsonify(row.to_dict() if row else {})


# ── Teachers ──────────────────────────────────────────────────
@public_bp.get("/api/teachers")
def get_teachers():
    rows = Teacher.query.filter_by(is_active=True).order_by(Teacher.full_name).all()
    return jsonify([t.to_dict() for t in rows])


# ── Classes ───────────────────────────────────────────────────
@public_bp.get("/api/classes")
def get_classes():
    from datetime import datetime
    year = request.args.get("year", datetime.now().year, type=int)
    rows = (Class.query
            .filter_by(academic_year=year)
            .order_by(Class.grade, Class.section)
            .all())
    return jsonify([c.to_dict() for c in rows])


# ── Achievements ──────────────────────────────────────────────
@public_bp.get("/api/achievements")
def get_achievements():
    q = Achievement.query
    if lvl := request.args.get("level"):
        q = q.filter_by(level=lvl)
    if yr := request.args.get("year", type=int):
        q = q.filter_by(achieved_year=yr)
    rows = q.order_by(Achievement.achieved_year.desc(), Achievement.place_number).all()
    return jsonify([a.to_dict() for a in rows])


@public_bp.get("/api/achievements/leaderboard")
def get_leaderboard():
    """Top-10 students by total achievement count, optional year filter."""
    yr  = request.args.get("year", type=int)
    q   = db.session.query(
        Achievement.student_name,
        Achievement.class_grade,
        Achievement.class_section,
        func.count(Achievement.id).label("total"),
        func.sum(func.if_(Achievement.place_number == 1, 1, 0)).label("gold"),
        func.sum(func.if_(Achievement.place_number == 2, 1, 0)).label("silver"),
        func.sum(func.if_(Achievement.place_number == 3, 1, 0)).label("bronze"),
    )
    if yr:
        q = q.filter(Achievement.achieved_year == yr)
    rows = (q.group_by(Achievement.student_name, Achievement.class_grade, Achievement.class_section)
             .order_by(desc("total"), desc("gold"))
             .limit(10).all())
    return jsonify([
        {"student_name": r.student_name, "class_grade": r.class_grade,
         "class_section": r.class_section, "total": r.total,
         "gold": int(r.gold or 0), "silver": int(r.silver or 0), "bronze": int(r.bronze or 0)}
        for r in rows
    ])


@public_bp.get("/api/achievements/by-class")
def get_achievements_by_class():
    """Best achievement per class — used in the classes table."""
    rows = (Achievement.query
            .filter(Achievement.class_grade.isnot(None))
            .order_by(Achievement.class_grade, Achievement.class_section,
                      Achievement.place_number, Achievement.achieved_year.desc())
            .all())
    grouped = {}
    for r in rows:
        key = f"{r.class_grade}-{r.class_section}"
        grouped.setdefault(key, []).append(r.to_dict())
    return jsonify(grouped)


@public_bp.get("/api/achievements/years")
def get_achievement_years():
    rows = (db.session.query(Achievement.achieved_year)
            .distinct().order_by(Achievement.achieved_year.desc()).all())
    return jsonify([r[0] for r in rows])


# ── News ──────────────────────────────────────────────────────
@public_bp.get("/api/news")
def get_news():
    page     = request.args.get("page", 1, type=int)
    per_page = min(20, request.args.get("per_page", 9, type=int))
    q        = News.query.filter_by(is_published=True).order_by(News.news_date.desc())
    return jsonify(paginate(q, page, per_page))


@public_bp.get("/api/news/<int:nid>")
def get_news_single(nid):
    row = News.query.filter_by(id=nid, is_published=True).first()
    if not row:
        return err("Not found", 404)
    return jsonify(row.to_dict())


# ── Announcements ─────────────────────────────────────────────
@public_bp.get("/api/announcements")
def get_announcements():
    today = date.today()
    rows  = (Announcement.query
             .filter_by(is_active=True)
             .filter((Announcement.expires_date == None) | (Announcement.expires_date >= today))
             .order_by(Announcement.published_date.desc())
             .all())
    return jsonify([a.to_dict() for a in rows])


# ── Gallery ───────────────────────────────────────────────────
@public_bp.get("/api/gallery")
def get_gallery():
    albums = GalleryAlbum.query.order_by(GalleryAlbum.event_date.desc()).all()
    return jsonify([a.to_dict() for a in albums])


# ── FAQ ───────────────────────────────────────────────────────
@public_bp.get("/api/faq")
def get_faq():
    rows = FAQ.query.filter_by(is_active=True).order_by(FAQ.sort_order).all()
    return jsonify([f.to_dict() for f in rows])


# ── Graduates ─────────────────────────────────────────────────
@public_bp.get("/api/graduates")
def get_graduates():
    rows = (Graduate.query.filter_by(is_approved=True)
            .order_by(Graduate.graduated_year.desc()).all())
    return jsonify([g.to_dict() for g in rows])


@public_bp.post("/api/graduates")
def submit_graduate():
    d    = request.get_json(silent=True) or {}
    name = (d.get("full_name") or "").strip()
    year = d.get("graduated_year")
    if not name or not year:
        return err("Нэр болон он заавал оруулна уу", 422)
    try:
        year = int(year)
        if not (2019 <= year <= 2099):
            raise ValueError
    except (ValueError, TypeError):
        return err("Он буруу байна", 422)
    g = Graduate(
        full_name      = name[:150],
        graduated_year = year,
        current_place  = (d.get("current_place") or "")[:255],
        message        = (d.get("message") or "")[:500],
        is_approved    = False,
    )
    db.session.add(g)
    db.session.commit()
    return ok(message="Таны мэдээлэл хүлээн авлаа. Admin зөвшөөрсний дараа харагдана."), 201
