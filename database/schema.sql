CREATE DATABASE IF NOT EXISTS doloodoi_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE doloodoi_db;

CREATE TABLE IF NOT EXISTS school_info (
    id            TINYINT UNSIGNED NOT NULL DEFAULT 1,
    full_name     VARCHAR(255)     NOT NULL,
    founded_date  DATE,
    vision        TEXT,
    mission       TEXT,
    values_text   TEXT,
    district      VARCHAR(100)     NOT NULL DEFAULT '',
    street        VARCHAR(150)     NOT NULL DEFAULT '',
    building      VARCHAR(50)      NOT NULL DEFAULT '',
    phone         VARCHAR(20)      NOT NULL DEFAULT '',
    email         VARCHAR(150)     NOT NULL DEFAULT '',
    facebook_url  VARCHAR(300),
    logo_path     VARCHAR(300),
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_school     PRIMARY KEY (id),
    CONSTRAINT chk_school_id CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS school_photos (
    id         INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    photo_path VARCHAR(300)      NOT NULL,
    caption    VARCHAR(255),
    photo_type ENUM('exterior','interior','event','other') NOT NULL DEFAULT 'other',
    sort_order SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_photo_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS director (
    id            TINYINT UNSIGNED NOT NULL DEFAULT 1,
    full_name     VARCHAR(150)     NOT NULL,
    biography     TEXT,
    photo_path    VARCHAR(300),
    greeting_text TEXT,
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_director     PRIMARY KEY (id),
    CONSTRAINT chk_director_id CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS teachers (
    id               INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    full_name        VARCHAR(150)  NOT NULL,
    subject          VARCHAR(150)  NOT NULL,
    degree           ENUM('bachelor','master','doctorate','other') NOT NULL DEFAULT 'bachelor',
    experience_years TINYINT UNSIGNED NOT NULL DEFAULT 0,
    photo_path       VARCHAR(300),
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_teacher_active (is_active),
    INDEX idx_teacher_name   (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS classes (
    id            INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    grade         TINYINT UNSIGNED NOT NULL COMMENT '1-12',
    section       VARCHAR(5)       NOT NULL COMMENT 'а б в ...',
    teacher_id    INT UNSIGNED,
    academic_year YEAR             NOT NULL,
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_class         UNIQUE  (grade, section, academic_year),
    CONSTRAINT fk_class_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_grade        CHECK (grade BETWEEN 1 AND 12),
    INDEX idx_class_grade (grade),
    INDEX idx_class_year  (academic_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    title        VARCHAR(255) NOT NULL,
    content      TEXT         NOT NULL,
    news_date    DATE         NOT NULL,
    photo_path   VARCHAR(300),
    is_published BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_news_date      (news_date DESC),
    INDEX idx_news_published (is_published)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS achievements (
    id            INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    competition   VARCHAR(255)     NOT NULL,
    student_name  VARCHAR(150)     NOT NULL,
    class_grade   TINYINT UNSIGNED COMMENT 'Ямар ангийн сурагч',
    class_section VARCHAR(5)       COMMENT 'Бүлэг',
    award         VARCHAR(150)     NOT NULL,
    place_number  TINYINT UNSIGNED COMMENT '1 2 3',
    achieved_year YEAR             NOT NULL,
    level         ENUM('school','district','city','national','international') NOT NULL DEFAULT 'school',
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_ach_year    (achieved_year DESC),
    INDEX idx_ach_level   (level),
    INDEX idx_ach_grade   (class_grade),
    INDEX idx_ach_student (student_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS announcements (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    title          VARCHAR(255) NOT NULL,
    content        TEXT         NOT NULL,
    published_date DATE         NOT NULL,
    expires_date   DATE,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT chk_ann_dates CHECK (expires_date IS NULL OR expires_date >= published_date),
    INDEX idx_ann_date   (published_date DESC),
    INDEX idx_ann_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS gallery_albums (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(150) NOT NULL,
    event_date  DATE,
    description TEXT,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_album_date (event_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS gallery_photos (
    id         INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    album_id   INT UNSIGNED      NOT NULL,
    photo_path VARCHAR(300)      NOT NULL,
    caption    VARCHAR(255),
    sort_order SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_gallery_album FOREIGN KEY (album_id) REFERENCES gallery_albums(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_gallery_album (album_id),
    INDEX idx_gallery_sort  (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS faq (
    id          INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    question    TEXT              NOT NULL,
    answer      TEXT              NOT NULL,
    question_en TEXT,
    answer_en   TEXT,
    sort_order  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    is_active   BOOLEAN           NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_faq_sort   (sort_order),
    INDEX idx_faq_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS graduates (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    full_name      VARCHAR(150) NOT NULL,
    graduated_year YEAR         NOT NULL,
    current_place  VARCHAR(255),
    message        TEXT,
    is_approved    BOOLEAN      NOT NULL DEFAULT FALSE,
    submitted_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at    TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_grad_year     (graduated_year DESC),
    INDEX idx_grad_approved (is_approved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS admins (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username      VARCHAR(60)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt only',
    email         VARCHAR(150) NOT NULL,
    role          ENUM('superadmin','admin') NOT NULL DEFAULT 'admin',
    last_login    TIMESTAMP,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_admin_username UNIQUE (username),
    CONSTRAINT uq_admin_email    UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS admin_sessions (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    admin_id   INT UNSIGNED NOT NULL,
    token_hash VARCHAR(255) NOT NULL COMMENT 'SHA-256 of raw token',
    ip_address VARCHAR(45)  NOT NULL,
    user_agent VARCHAR(300),
    expires_at TIMESTAMP    NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_session_admin FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE,
    INDEX idx_session_token   (token_hash),
    INDEX idx_session_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_log (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    admin_id   INT UNSIGNED,
    table_name VARCHAR(60)     NOT NULL,
    action     ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    record_id  INT UNSIGNED,
    note       VARCHAR(300),
    ip_address VARCHAR(45),
    created_at TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_audit_table (table_name, created_at DESC),
    INDEX idx_audit_admin (admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO admins (username, password_hash, email, role, is_active) VALUES
('Turuu',
 '$2b$12$icabI94UoGwmNE5Bn6ru4OAPMId1uFNp8XP8azk8qxpqA3z8jJU8i',
 'turuu@doloodoi.mn', 'superadmin', 1),
('Misheel',
 '$2b$12$1EBMZ9L/mLQ6s8ATMuGASeZwPZgl3Jc.Gn/UCax7hoBHVIMOlE6H.',
 'misheel@doloodoi.mn', 'admin', 1)
ON DUPLICATE KEY UPDATE username = username;

INSERT INTO school_info (id, full_name, founded_date, district, street, building, phone, email)
VALUES (1,'Долоодой Сургууль','2019-08-01','Дорнод аймаг','Хэрлэн сум','1','99001234','info@doloodoi.mn')
ON DUPLICATE KEY UPDATE id = id;

INSERT INTO faq (question, answer, question_en, answer_en, sort_order) VALUES
('Элсэлт хэзээ эхэлдэг вэ?','Жил бүр 8-р сарын эхээр эхэлдэг.','When does enrollment start?','Enrollment opens in early August each year.',1),
('Сургалтын хуваарь ямар байдаг вэ?','08:00–17:00 цагийн хооронд явагдана.','What are the school hours?','Classes run from 08:00 to 17:00.',2),
('Сургуульд хэрхэн элсэх вэ?','Иргэний үнэмлэх, төрсний гэрчилгээ, өмнөх сургуулийн тодорхойлолт авчирна уу.','How do I enroll?','Bring parent ID, birth certificate, and a reference from the previous school.',3),
('Сургалтын төлбөр хэд вэ?','Утсаар эсвэл биечлэн лавлана уу.','What is the tuition?','Please contact us by phone or visit the school.',4),
('Дугуйлан байдаг уу?','Тийм! Спорт, урлаг, хөгжим, шинжлэх ухааны дугуйлан ажилладаг.','Are there clubs?','Yes! Sports, arts, music and science clubs are available.',5);
