import sys
from datetime import UTC, datetime

from flask import Flask, redirect, request, url_for, flash
from config import Config
from models import db
from routes.public import public_bp
from routes.admin import admin_bp
from services.seed import initialize_sample_data


def ensure_database_columns():
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    table_columns = {
        table_name: {column["name"] for column in inspector.get_columns(table_name)}
        for table_name in inspector.get_table_names()
    }
    migrations = {
        "articles": {"image_filename": "ALTER TABLE articles ADD COLUMN image_filename VARCHAR(200)"},
        "events": {"image_filename": "ALTER TABLE events ADD COLUMN image_filename VARCHAR(200)"},
        "feedback": {"status": "ALTER TABLE feedback ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'approved'"},
        "gallery": {"event_id": "ALTER TABLE gallery ADD COLUMN event_id INTEGER"},
    }
    for table_name, columns in migrations.items():
        existing_columns = table_columns.get(table_name, set())
        for column_name, statement in columns.items():
            if column_name not in existing_columns:
                db.session.execute(text(statement))
    db.session.commit()


def create_app(config_class=Config, config_overrides=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)
    if "pytest" in sys.modules:
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            WTF_CSRF_ENABLED=False,
        )
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_database_columns()

        # Ensure a default academic admin account exists for demonstration
        from models import Admin
        Admin.create_default_admin()
        initialize_sample_data()

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now(UTC).year}

    @app.errorhandler(413)
    def file_too_large(error):
        # Large uploads are sent back with a friendly message instead of Flask's default error page.
        flash("The uploaded file is too large. Please upload an image smaller than 16 MB.", "error")
        return redirect(request.referrer or url_for("public.home"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
