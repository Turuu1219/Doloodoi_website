from datetime import datetime
from flask import Blueprint, request, jsonify, make_response

from backend.models.base    import db
from backend.models.models  import (Admin, AdminSession, SchoolInfo, SchoolPhoto,
                                     Director, Teacher, Class, News, Achievement,
                                     Announcement, GalleryAlbum, GalleryPhoto,
                                     FAQ, Graduate, AuditLog)
from backend.utils.auth     import (admin_required, superadmin_required,
                                     check_password, create_session, destroy_session)
from backend.utils.helpers  import ok, err, save_upload, log_audit, paginate, require_fields
from backend.config         import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.post("/login")
def admin_login():
    d = request.get_json(silent=True) or {}
    missing = require_fields(d, "username", "password")
    if missing:
        return err(f"Missing: {', '.join(missing)}", 422)
    admin = Admin.query.filter_by(username=d["username"], is_active=True).first()
    if not admin or not check_password(d["password"], admin.password_hash):
        return err("Нэвтрэх нэр эсвэл нууц үг буруу байна", 401)
    token = create_session(admin.id, request.remote_addr, request.user_agent.string)
    admin.last_login = datetime.utcnow()
    db.session.commit()
    resp = make_response(jsonify({"success": True, "username": admin.username, "role": admin.role}))
    resp.set_cookie("admin_token", token, httponly=True, samesite="Strict",
                    max_age=Config.SESSION_HOURS * 3600)
    return resp

@admin_bp.post("/logout")
@admin_required
def admin_logout():
    destroy_session(request.cookies.get("admin_token"))
    resp = make_response(jsonify({"success": True}))
    resp.delete_cookie("admin_token")
    return resp

@admin_bp.get("/me")
@admin_required
def admin_me():
    return jsonify({"username": request.admin.username, "role": request.admin.role})

@admin_bp.get("/stats")
@admin_required
def admin_stats():
    return jsonify({
        "teachers":           Teacher.query.filter_by(is_active=True).count(),
        "classes":            Class.query.count(),
        "news":               News.query.count(),
        "published_news":     News.query.filter_by(is_published=True).count(),
        "achievements":       Achievement.query.count(),
        "announcements":      Announcement.query.filter_by(is_active=True).count(),
        "gallery_albums":     GalleryAlbum.query.count(),
        "gallery_photos":     GalleryPhoto.query.count(),
        "graduates_pending":  Graduate.query.filter_by(is_approved=False).count(),
        "graduates_approved": Graduate.query.filter_by(is_approved=True).count(),
    })

@admin_bp.get("/school")
@admin_required
def admin_get_school():
    row = SchoolInfo.query.first()
    return jsonify(row.to_dict() if row else {})

@admin_bp.put("/school")
@admin_required
def admin_update_school():
    d         = request.form
    logo_path = save_upload(request.files.get("logo"), "logo")
    row       = SchoolInfo.query.first() or SchoolInfo(id=1)
    fields = ["full_name","founded_date","vision","mission","values_text",
              "district","street","building","phone","email","facebook_url"]
    for f in fields:
        if f in d:
            val = d[f]
            if f == "founded_date" and val == "":
                val = None
            setattr(row, f, val)

    if logo_path:
        row.logo_path = logo_path
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "school_info", "UPDATE", 1)
    return ok(message="Хадгалагдлаа")

@admin_bp.get("/school-photos")
@admin_required
def admin_get_school_photos():
    rows = SchoolPhoto.query.order_by(SchoolPhoto.sort_order).all()
    return jsonify([r.to_dict() for r in rows])

@admin_bp.post("/school-photos")
@admin_required
def admin_add_school_photo():
    path = save_upload(request.files.get("photo"), "school")
    if not path:
        return err("Зураг шаардлагатай")
    d   = request.form
    row = SchoolPhoto(photo_path=path, caption=d.get("caption",""),
                      photo_type=d.get("photo_type","other"),
                      sort_order=int(d.get("sort_order", 0)))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "school_photos", "INSERT", row.id)
    return ok({"id": row.id, "path": path}, status=201)

@admin_bp.delete("/school-photos/<int:pid>")
@admin_required
def admin_delete_school_photo(pid):
    row = SchoolPhoto.query.get_or_404(pid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "school_photos", "DELETE", pid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/director")
@admin_required
def admin_get_director():
    row = Director.query.first()
    return jsonify(row.to_dict() if row else {})


@admin_bp.put("/director")
@admin_required
def admin_update_director():
    d     = request.form
    photo = save_upload(request.files.get("photo"), "director")
    row   = Director.query.first() or Director(id=1)
    for f in ["full_name","biography","greeting_text"]:
        if f in d:
            setattr(row, f, d[f])
    if photo:
        row.photo_path = photo
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "director", "UPDATE", 1)
    return ok(message="Хадгалагдлаа")

@admin_bp.get("/teachers")
@admin_required
def admin_get_teachers():
    rows = Teacher.query.order_by(Teacher.full_name).all()
    return jsonify([t.to_dict() for t in rows])


@admin_bp.post("/teachers")
@admin_required
def admin_add_teacher():
    d     = request.form
    if not d.get("full_name") or not d.get("subject"):
        return err("Нэр болон хичээл шаардлагатай", 422)
    photo = save_upload(request.files.get("photo"), "teachers")
    row   = Teacher(full_name=d["full_name"], subject=d["subject"],
                    degree=d.get("degree","bachelor"),
                    experience_years=int(d.get("experience_years",0)),
                    photo_path=photo)
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "teachers", "INSERT", row.id)
    return ok({"id": row.id}, status=201)


@admin_bp.put("/teachers/<int:tid>")
@admin_required
def admin_update_teacher(tid):
    row   = Teacher.query.get_or_404(tid)
    d     = request.form
    photo = save_upload(request.files.get("photo"), "teachers")
    for f in ["full_name","subject","degree","experience_years"]:
        if f in d:
            setattr(row, f, d[f])
    if "is_active" in d:
        row.is_active = d["is_active"] in ("1","true","True")
    if photo:
        row.photo_path = photo
    db.session.commit()
    log_audit(request.admin.id, "teachers", "UPDATE", tid)
    return ok(message="Хадгалагдлаа")


@admin_bp.delete("/teachers/<int:tid>")
@admin_required
def admin_delete_teacher(tid):
    row = Teacher.query.get_or_404(tid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "teachers", "DELETE", tid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/classes")
@admin_required
def admin_get_classes():
    rows = Class.query.order_by(Class.grade, Class.section).all()
    return jsonify([c.to_dict() for c in rows])

@admin_bp.post("/classes")
@admin_required
def admin_add_class():
    d = request.get_json(silent=True) or {}
    missing = require_fields(d, "grade", "section", "academic_year")
    if missing:
        return err(f"Шаардлагатай: {', '.join(missing)}", 422)
    row = Class(grade=d["grade"], section=d["section"],
                teacher_id=d.get("teacher_id"), academic_year=d["academic_year"])
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "classes", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.put("/classes/<int:cid>")
@admin_required
def admin_update_class(cid):
    row = Class.query.get_or_404(cid)
    d   = request.get_json(silent=True) or {}
    for f in ["grade","section","academic_year","teacher_id"]:
        if f in d:
            setattr(row, f, d[f])
    db.session.commit()
    log_audit(request.admin.id, "classes", "UPDATE", cid)
    return ok(message="Хадгалагдлаа")

@admin_bp.delete("/classes/<int:cid>")
@admin_required
def admin_delete_class(cid):
    row = Class.query.get_or_404(cid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "classes", "DELETE", cid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/news")
@admin_required
def admin_get_news():
    page = request.args.get("page", 1, type=int)
    q    = News.query.order_by(News.news_date.desc())
    return jsonify(paginate(q, page, 20))

@admin_bp.post("/news")
@admin_required
def admin_add_news():
    d     = request.form
    missing = require_fields(d, "title", "content", "news_date")
    if missing:
        return err(f"Шаардлагатай: {', '.join(missing)}", 422)
    photo = save_upload(request.files.get("photo"), "news")
    row   = News(title=d["title"], content=d["content"], news_date=d["news_date"],
                 photo_path=photo, is_published=d.get("is_published","1") in ("1","true"))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "news", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.put("/news/<int:nid>")
@admin_required
def admin_update_news(nid):
    row   = News.query.get_or_404(nid)
    d     = request.form
    photo = save_upload(request.files.get("photo"), "news")
    for f in ["title","content","news_date"]:
        if f in d:
            setattr(row, f, d[f])
    if "is_published" in d:
        row.is_published = d["is_published"] in ("1","true","True")
    if photo:
        row.photo_path = photo
    db.session.commit()
    log_audit(request.admin.id, "news", "UPDATE", nid)
    return ok(message="Хадгалагдлаа")

@admin_bp.delete("/news/<int:nid>")
@admin_required
def admin_delete_news(nid):
    row = News.query.get_or_404(nid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "news", "DELETE", nid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/achievements")
@admin_required
def admin_get_achievements():
    rows = Achievement.query.order_by(Achievement.achieved_year.desc()).all()
    return jsonify([a.to_dict() for a in rows])

@admin_bp.post("/achievements")
@admin_required
def admin_add_achievement():
    d = request.get_json(silent=True) or {}
    missing = require_fields(d, "competition", "student_name", "award", "achieved_year")
    if missing:
        return err(f"Шаардлагатай: {', '.join(missing)}", 422)
    row = Achievement(competition=d["competition"], student_name=d["student_name"],
                      class_grade=d.get("class_grade"), class_section=d.get("class_section"),
                      award=d["award"], place_number=d.get("place_number"),
                      achieved_year=d["achieved_year"], level=d.get("level","school"))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "achievements", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.put("/achievements/<int:aid>")
@admin_required
def admin_update_achievement(aid):
    row = Achievement.query.get_or_404(aid)
    d   = request.get_json(silent=True) or {}
    for f in ["competition","student_name","class_grade","class_section",
              "award","place_number","achieved_year","level"]:
        if f in d:
            setattr(row, f, d[f])
    db.session.commit()
    log_audit(request.admin.id, "achievements", "UPDATE", aid)
    return ok(message="Хадгалагдлаа")

@admin_bp.delete("/achievements/<int:aid>")
@admin_required
def admin_delete_achievement(aid):
    row = Achievement.query.get_or_404(aid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "achievements", "DELETE", aid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/announcements")
@admin_required
def admin_get_announcements():
    rows = Announcement.query.order_by(Announcement.published_date.desc()).all()
    return jsonify([a.to_dict() for a in rows])

@admin_bp.post("/announcements")
@admin_required
def admin_add_announcement():
    d = request.get_json(silent=True) or {}
    missing = require_fields(d, "title", "content", "published_date")
    if missing:
        return err(f"Шаардлагатай: {', '.join(missing)}", 422)
    row = Announcement(title=d["title"], content=d["content"],
                       published_date=d["published_date"],
                       expires_date=d.get("expires_date"),
                       is_active=d.get("is_active", True))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "announcements", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.put("/announcements/<int:aid>")
@admin_required
def admin_update_announcement(aid):
    row = Announcement.query.get_or_404(aid)
    d   = request.get_json(silent=True) or {}
    for f in ["title","content","published_date","expires_date","is_active"]:
        if f in d:
            setattr(row, f, d[f])
    db.session.commit()
    log_audit(request.admin.id, "announcements", "UPDATE", aid)
    return ok(message="Хадгалагдлаа")

@admin_bp.delete("/announcements/<int:aid>")
@admin_required
def admin_delete_announcement(aid):
    row = Announcement.query.get_or_404(aid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "announcements", "DELETE", aid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/gallery/albums")
@admin_required
def admin_get_albums():
    rows = GalleryAlbum.query.order_by(GalleryAlbum.event_date.desc()).all()
    return jsonify([a.to_dict() for a in rows])

@admin_bp.post("/gallery/albums")
@admin_required
def admin_add_album():
    d   = request.get_json(silent=True) or {}
    row = GalleryAlbum(name=d.get("name","Цомог"),
                       event_date=d.get("event_date"),
                       description=d.get("description"))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "gallery_albums", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.delete("/gallery/albums/<int:aid>")
@admin_required
def admin_delete_album(aid):
    row = GalleryAlbum.query.get_or_404(aid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "gallery_albums", "DELETE", aid)
    return ok(message="Устгагдлаа")

@admin_bp.post("/gallery/photos")
@admin_required
def admin_add_gallery_photo():
    path = save_upload(request.files.get("photo"), "gallery")
    if not path:
        return err("Зураг шаардлагатай")
    d   = request.form
    row = GalleryPhoto(album_id=d.get("album_id"), photo_path=path,
                       caption=d.get("caption",""),
                       sort_order=int(d.get("sort_order",0)))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "gallery_photos", "INSERT", row.id)
    return ok({"id": row.id, "path": path}, status=201)

@admin_bp.delete("/gallery/photos/<int:pid>")
@admin_required
def admin_delete_gallery_photo(pid):
    row = GalleryPhoto.query.get_or_404(pid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "gallery_photos", "DELETE", pid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/faq")
@admin_required
def admin_get_faq():
    rows = FAQ.query.order_by(FAQ.sort_order).all()
    return jsonify([f.to_dict() for f in rows])

@admin_bp.post("/faq")
@admin_required
def admin_add_faq():
    d   = request.get_json(silent=True) or {}
    row = FAQ(question=d.get("question",""), answer=d.get("answer",""),
              question_en=d.get("question_en"), answer_en=d.get("answer_en"),
              sort_order=d.get("sort_order",0))
    db.session.add(row)
    db.session.commit()
    log_audit(request.admin.id, "faq", "INSERT", row.id)
    return ok({"id": row.id}, status=201)

@admin_bp.put("/faq/<int:fid>")
@admin_required
def admin_update_faq(fid):
    row = FAQ.query.get_or_404(fid)
    d   = request.get_json(silent=True) or {}
    for f in ["question","answer","question_en","answer_en","sort_order","is_active"]:
        if f in d:
            setattr(row, f, d[f])
    db.session.commit()
    log_audit(request.admin.id, "faq", "UPDATE", fid)
    return ok(message="Хадгалагдлаа")

@admin_bp.delete("/faq/<int:fid>")
@admin_required
def admin_delete_faq(fid):
    row = FAQ.query.get_or_404(fid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "faq", "DELETE", fid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/graduates")
@admin_required
def admin_get_graduates():
    rows = Graduate.query.order_by(Graduate.submitted_at.desc()).all()
    return jsonify([g.to_dict(admin=True) for g in rows])

@admin_bp.post("/graduates/<int:gid>/approve")
@admin_required
def admin_approve_graduate(gid):
    row = Graduate.query.get_or_404(gid)
    row.is_approved = True
    row.approved_at = datetime.utcnow()
    db.session.commit()
    log_audit(request.admin.id, "graduates", "UPDATE", gid, "approved")
    return ok(message="Зөвшөөрлөө")

@admin_bp.delete("/graduates/<int:gid>")
@admin_required
def admin_delete_graduate(gid):
    row = Graduate.query.get_or_404(gid)
    db.session.delete(row)
    db.session.commit()
    log_audit(request.admin.id, "graduates", "DELETE", gid)
    return ok(message="Устгагдлаа")

@admin_bp.get("/audit-log")
@superadmin_required
def admin_get_audit_log():
    page = request.args.get("page", 1, type=int)
    q    = AuditLog.query.order_by(AuditLog.created_at.desc())
    total = q.count()
    rows  = q.offset((page-1)*50).limit(50).all()
    return jsonify({
        "items": [{"id":r.id,"admin_id":r.admin_id,"table_name":r.table_name,
                   "action":r.action,"record_id":r.record_id,"note":r.note,
                   "ip_address":r.ip_address,
                   "created_at":r.created_at.isoformat() if r.created_at else None}
                  for r in rows],
        "total": total, "page": page
    })
