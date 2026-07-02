import os

basedir = os.path.abspath(os.path.dirname(__file__))


def database_uri():
    uri = os.environ.get("DATABASE_URL")
    if uri:
        if uri.startswith("postgres://"):
            return uri.replace("postgres://", "postgresql://", 1)
        return uri
    return "sqlite:///" + os.path.join(basedir, "database", "ai_solutions.db")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-for-production")
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(basedir, "static", "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
