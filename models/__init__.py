from datetime import UTC, datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_default_admin(cls):
        default_username = "admin"
        default_password = "Password123!"
        if not cls.query.filter_by(username=default_username).first():
            admin = cls(username=default_username)
            admin.set_password(default_password)
            db.session.add(admin)
            db.session.commit()


class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    job_details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


class GalleryItem(db.Model):
    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(220), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    event = db.relationship("Event", back_populates="gallery_items")


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    summary = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    gallery_items = db.relationship(
        "GalleryItem",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="GalleryItem.created_at.desc()",
    )
