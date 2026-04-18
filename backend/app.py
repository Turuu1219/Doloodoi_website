"""
backend/app.py
Flask application factory.
Registers blueprints, extensions, error handlers, Swagger UI.
"""
import os, logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger

from backend.config           import Config
from backend.models.base      import db
from backend.routes.public    import public_bp
from backend.routes.admin     import admin_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"))
STATIC_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "static"))


def create_app() -> Flask:
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    limiter = Limiter(key_func=get_remote_address, app=app,
                      default_limits=[Config.RATELIMIT_DEFAULT],
                      storage_uri=Config.RATELIMIT_STORAGE_URL)
    limiter.limit(Config.RATELIMIT_LOGIN)(admin_bp.view_functions["admin.admin_login"])

    # Swagger UI
    Swagger(app, template={
        "swagger": "2.0",
        "info": {"title": "Долоодой Сургуулийн API", "version": "3.0",
                 "description": "REST API — public + admin endpoints"},
        "basePath": "/",
        "securityDefinitions": {
            "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "admin_token"}
        },
    })

    # Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"success": False, "error": "File too large (max 10 MB)"}), 413

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"success": False, "error": "Хэт олон хүсэлт. Түр хүлээнэ үү."}), 429

    @app.errorhandler(500)
    def server_error(e):
        logger.error("500: %s", e)
        return jsonify({"success": False, "error": "Серверийн алдаа гарлаа"}), 500

    # Request logging
    @app.before_request
    def log_req():
        from flask import request
        logger.info("→ %s %s | %s", request.method, request.path, request.remote_addr)

    # Frontend routes
    @app.get("/")
    def serve_index():
        return send_from_directory(TEMPLATE_DIR, "index.html")

    @app.get("/admin")
    def serve_admin():
        return send_from_directory(TEMPLATE_DIR, "admin.html")

    @app.get("/static/<path:path>")
    def serve_static(path):
        return send_from_directory(STATIC_DIR, path)

    logger.info("✅ App ready | debug=%s", Config.DEBUG)
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
