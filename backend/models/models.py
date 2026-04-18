"""
backend/models/models.py
SQLAlchemy ORM models — mirror the schema.sql tables exactly.
"""
from datetime import datetime
from backend.models.base import db


class SchoolInfo(db.Model):
    __tablename__ = "school_info"
    id            = db.Column(db.SmallInteger, primary_key=True, default=1)
    full_name     = db.Column(db.String(255), nullable=False)
    founded_date  = db.Column(db.Date)
    vision        = db.Column(db.Text)
    mission       = db.Column(db.Text)
    values_text   = db.Column(db.Text)
    district      = db.Column(db.String(100), nullable=False, default="")
    street        = db.Column(db.String(150), nullable=False, default="")
    building      = db.Column(db.String(50),  nullable=False, default="")
    phone         = db.Column(db.String(20),  nullable=False, default="")
    email         = db.Column(db.String(150), nullable=False, default="")
    facebook_url  = db.Column(db.String(300))
    logo_path     = db.Column(db.String(300))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: (getattr(self, c.name).isoformat()
                         if isinstance(getattr(self, c.name), (datetime, )) else getattr(self, c.name))
                for c in self.__table__.columns}


class SchoolPhoto(db.Model):
    __tablename__ = "school_photos"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_path = db.Column(db.String(300), nullable=False)
    caption    = db.Column(db.String(255))
    photo_type = db.Column(db.Enum("exterior","interior","event","other"), default="other")
    sort_order = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"photo_path":self.photo_path,"caption":self.caption,"photo_type":self.photo_type,"sort_order":self.sort_order}


class Director(db.Model):
    __tablename__ = "director"
    id            = db.Column(db.SmallInteger, primary_key=True, default=1)
    full_name     = db.Column(db.String(150), nullable=False)
    biography     = db.Column(db.Text)
    photo_path    = db.Column(db.String(300))
    greeting_text = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"full_name":self.full_name,"biography":self.biography,"photo_path":self.photo_path,"greeting_text":self.greeting_text}


class Teacher(db.Model):
    __tablename__ = "teachers"
    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name        = db.Column(db.String(150), nullable=False)
    subject          = db.Column(db.String(150), nullable=False)
    degree           = db.Column(db.Enum("bachelor","master","doctorate","other"), default="bachelor")
    experience_years = db.Column(db.SmallInteger, default=0)
    photo_path       = db.Column(db.String(300))
    is_active        = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    classes          = db.relationship("Class", backref="teacher", lazy=True)

    def to_dict(self):
        return {"id":self.id,"full_name":self.full_name,"subject":self.subject,
                "degree":self.degree,"experience_years":self.experience_years,
                "photo_path":self.photo_path,"is_active":self.is_active}


class Class(db.Model):
    __tablename__  = "classes"
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade          = db.Column(db.SmallInteger, nullable=False)
    section        = db.Column(db.String(5),  nullable=False)
    teacher_id     = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL", onupdate="CASCADE"))
    academic_year  = db.Column(db.SmallInteger, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"grade":self.grade,"section":self.section,
                "teacher_name":self.teacher.full_name if self.teacher else None,
                "academic_year":self.academic_year}


class News(db.Model):
    __tablename__ = "news"
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title        = db.Column(db.String(255), nullable=False)
    content      = db.Column(db.Text,        nullable=False)
    news_date    = db.Column(db.Date,        nullable=False)
    photo_path   = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"title":self.title,"content":self.content,
                "news_date":self.news_date.isoformat() if self.news_date else None,
                "photo_path":self.photo_path,"is_published":self.is_published}


class Achievement(db.Model):
    __tablename__ = "achievements"
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competition   = db.Column(db.String(255), nullable=False)
    student_name  = db.Column(db.String(150), nullable=False)
    class_grade   = db.Column(db.SmallInteger)
    class_section = db.Column(db.String(5))
    award         = db.Column(db.String(150), nullable=False)
    place_number  = db.Column(db.SmallInteger)
    achieved_year = db.Column(db.SmallInteger, nullable=False)
    level         = db.Column(db.Enum("school","district","city","national","international"), default="school")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"competition":self.competition,"student_name":self.student_name,
                "class_grade":self.class_grade,"class_section":self.class_section,
                "award":self.award,"place_number":self.place_number,
                "achieved_year":self.achieved_year,"level":self.level}


class Announcement(db.Model):
    __tablename__ = "announcements"
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title          = db.Column(db.String(255), nullable=False)
    content        = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.Date, nullable=False)
    expires_date   = db.Column(db.Date)
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"title":self.title,"content":self.content,
                "published_date":self.published_date.isoformat() if self.published_date else None,
                "expires_date":self.expires_date.isoformat() if self.expires_date else None,
                "is_active":self.is_active}


class GalleryAlbum(db.Model):
    __tablename__ = "gallery_albums"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column(db.String(150), nullable=False)
    event_date  = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    photos      = db.relationship("GalleryPhoto", backref="album", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {"id":self.id,"name":self.name,
                "event_date":self.event_date.isoformat() if self.event_date else None,
                "description":self.description,
                "photos":[p.to_dict() for p in self.photos]}


class GalleryPhoto(db.Model):
    __tablename__ = "gallery_photos"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_id   = db.Column(db.Integer, db.ForeignKey("gallery_albums.id", ondelete="CASCADE"), nullable=False)
    photo_path = db.Column(db.String(300), nullable=False)
    caption    = db.Column(db.String(255))
    sort_order = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"album_id":self.album_id,"photo_path":self.photo_path,
                "caption":self.caption,"sort_order":self.sort_order}


class FAQ(db.Model):
    __tablename__ = "faq"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question    = db.Column(db.Text, nullable=False)
    answer      = db.Column(db.Text, nullable=False)
    question_en = db.Column(db.Text)
    answer_en   = db.Column(db.Text)
    sort_order  = db.Column(db.SmallInteger, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id":self.id,"question":self.question,"answer":self.answer,
                "question_en":self.question_en,"answer_en":self.answer_en,"sort_order":self.sort_order}


class Graduate(db.Model):
    __tablename__ = "graduates"
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name      = db.Column(db.String(150), nullable=False)
    graduated_year = db.Column(db.SmallInteger, nullable=False)
    current_place  = db.Column(db.String(255))
    message        = db.Column(db.Text)
    is_approved    = db.Column(db.Boolean, default=False)
    submitted_at   = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at    = db.Column(db.DateTime)

    def to_dict(self, admin=False):
        d = {"id":self.id,"full_name":self.full_name,"graduated_year":self.graduated_year,
             "current_place":self.current_place,"message":self.message}
        if admin:
            d["is_approved"]  = self.is_approved
            d["submitted_at"] = self.submitted_at.isoformat() if self.submitted_at else None
        return d


class Admin(db.Model):
    __tablename__ = "admins"
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username      = db.Column(db.String(60),  nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True)
    role          = db.Column(db.Enum("superadmin","admin"), default="admin")
    last_login    = db.Column(db.DateTime)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    sessions      = db.relationship("AdminSession", backref="admin", lazy=True, cascade="all, delete-orphan")


class AdminSession(db.Model):
    __tablename__ = "admin_sessions"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id   = db.Column(db.Integer, db.ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45),  nullable=False)
    user_agent = db.Column(db.String(300))
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    admin_id   = db.Column(db.Integer)
    table_name = db.Column(db.String(60),  nullable=False)
    action     = db.Column(db.Enum("INSERT","UPDATE","DELETE"), nullable=False)
    record_id  = db.Column(db.Integer)
    note       = db.Column(db.String(300))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
