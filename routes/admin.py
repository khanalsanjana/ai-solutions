import random
import csv
import io
from datetime import UTC, datetime
from pathlib import Path

from flask import Blueprint, Response, current_app, render_template, request, redirect, url_for, flash, session
from models import Admin, Inquiry, Article, Feedback, Event, GalleryItem
from utils.forms import AdminLoginForm
from werkzeug.utils import secure_filename
import os
from models import db
from services.analytics import inquiry_summary
from functools import wraps

admin_bp = Blueprint("admin", __name__)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("admin_authenticated"):
            flash("Please sign in to access the admin dashboard.", "warning")
            return redirect(url_for("admin.login"))
        return view(**kwargs)

    wrapped_view.__name__ = view.__name__
    return wrapped_view


def generate_captcha():
    a = random.randint(2, 9)
    b = random.randint(1, 8)
    session["captcha_expected"] = str(a + b)
    return f"What is {a} + {b}?"


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def unique_upload_name(filename):
    base_name = secure_filename(filename)
    stem = Path(base_name).stem or "gallery-image"
    suffix = Path(base_name).suffix.lower()
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    return f"{stem}-{timestamp}{suffix}"


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    # Generate a fresh CAPTCHA for GET requests so question changes on each visit
    if request.method == "GET":
        captcha_question = generate_captcha()
        session["captcha_question"] = captcha_question
    else:
        captcha_question = session.get("captcha_question") or generate_captcha()
        session["captcha_question"] = captcha_question

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        captcha_answer = form.captcha_answer.data.strip()
        admin = Admin.query.filter_by(username=username).first()

        if captcha_answer != session.get("captcha_expected"):
            session.pop("captcha_expected", None)
            session.pop("captcha_question", None)
            form.captcha_answer.errors.append("CAPTCHA answer is incorrect. Please try again.")
            captcha_question = generate_captcha()
            session["captcha_question"] = captcha_question
            return render_template("admin/login.html", form=form, captcha_question=captcha_question), 400

        if admin and admin.check_password(password):
            session["admin_authenticated"] = True
            session["admin_username"] = admin.username
            flash("Welcome to the AI-Solutions admin dashboard.", "success")
            return redirect(url_for("admin.dashboard"))

        form.username.errors.append("Username or password is incorrect.")
        form.password.errors.append("Username or password is incorrect.")
        session.pop("captcha_expected", None)
        session.pop("captcha_question", None)
        captcha_question = generate_captcha()
        session["captcha_question"] = captcha_question
        return render_template("admin/login.html", form=form, captcha_question=captcha_question), 400

    return render_template("admin/login.html", form=form, captcha_question=captcha_question)


@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    analytics = inquiry_summary()
    feedback_status_counts = {
        "pending": Feedback.query.filter_by(status="pending").count(),
        "approved": Feedback.query.filter_by(status="approved").count(),
        "rejected": Feedback.query.filter_by(status="rejected").count(),
    }
    pending_feedback = Feedback.query.filter_by(status="pending").order_by(Feedback.created_at.desc()).limit(5).all()
    return render_template(
        "admin/dashboard.html",
        total_inquiries=analytics["total"],
        recent_inquiries=analytics["recent"],
        country_counts=analytics["country_counts"],
        feedback_status_counts=feedback_status_counts,
        pending_feedback=pending_feedback,
    )


@admin_bp.route("/inquiries")
@login_required
def inquiries():
    all_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin/inquiries.html", inquiries=all_inquiries)


@admin_bp.route("/inquiries/<int:inquiry_id>/delete", methods=["POST"])
@login_required
def delete_inquiry(inquiry_id):
    inquiry = db.get_or_404(Inquiry, inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()
    flash("Inquiry removed.", "info")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/inquiries/export")
@login_required
def export_inquiries():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Phone", "Company", "Country", "Job Title", "Job Details", "Submitted At"])
    for inquiry in Inquiry.query.order_by(Inquiry.created_at.desc()).all():
        writer.writerow([
            inquiry.full_name,
            inquiry.email,
            inquiry.phone,
            inquiry.company,
            inquiry.country,
            inquiry.job_title,
            inquiry.job_details,
            inquiry.created_at.strftime("%Y-%m-%d %H:%M"),
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai-solutions-inquiries.csv"},
    )


@admin_bp.route("/articles", methods=["GET", "POST"])
@login_required
def manage_articles():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        content = request.form.get("content", "").strip()
        image = request.files.get("image")
        image_filename = None
        if title and summary and content:
            if image and image.filename:
                if not allowed_image(image.filename):
                    flash("Article image must be JPG, PNG, GIF, or WebP.", "error")
                    return redirect(url_for("admin.manage_articles"))
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                image_filename = unique_upload_name(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], image_filename))
            article = Article(title=title, summary=summary, content=content, image_filename=image_filename)
            db.session.add(article)
            db.session.commit()
            flash("Article published successfully.", "success")
            return redirect(url_for("admin.manage_articles"))
        flash("Please provide title, summary, and content.", "error")
    articles = Article.query.order_by(Article.published_at.desc()).all()
    return render_template("admin/articles.html", articles=articles)


@admin_bp.route("/articles/<int:article_id>/delete", methods=["POST"])
@login_required
def delete_article(article_id):
    article = db.get_or_404(Article, article_id)
    if article.image_filename:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], article.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(article)
    db.session.commit()
    flash("Article removed.", "info")
    return redirect(url_for("admin.manage_articles"))


@admin_bp.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        content = request.form.get("content", "").strip()
        image = request.files.get("image")
        if title and summary and content:
            if image and image.filename:
                if not allowed_image(image.filename):
                    flash("Article image must be JPG, PNG, GIF, or WebP.", "error")
                    return redirect(url_for("admin.edit_article", article_id=article.id))
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                new_filename = unique_upload_name(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename))
                if article.image_filename:
                    old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], article.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                article.image_filename = new_filename
            article.title = title
            article.summary = summary
            article.content = content
            db.session.commit()
            flash("Article updated.", "success")
            return redirect(url_for("admin.manage_articles"))
        flash("Please provide title, summary, and content.", "error")
    return render_template("admin/edit_article.html", article=article)


@admin_bp.route("/feedback", methods=["GET", "POST"])
@login_required
def manage_feedback():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        position = request.form.get("position", "").strip()
        comment = request.form.get("comment", "").strip()
        rating = request.form.get("rating", type=int)
        if customer_name and comment and rating and 1 <= rating <= 5:
            feedback = Feedback(customer_name=customer_name, position=position, comment=comment, rating=rating or 5, status="approved")
            db.session.add(feedback)
            db.session.commit()
            flash("Feedback entry added.", "success")
            return redirect(url_for("admin.manage_feedback"))
        flash("Customer name, comment, and a rating from 1 to 5 are required.", "error")
    feedback_items = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template("admin/feedback.html", feedback_items=feedback_items)


@admin_bp.route("/feedback/<int:feedback_id>/status", methods=["POST"])
@login_required
def update_feedback_status(feedback_id):
    feedback = db.get_or_404(Feedback, feedback_id)
    status = request.form.get("status", "").strip().lower()
    if status not in {"pending", "approved", "rejected"}:
        flash("Invalid feedback status.", "error")
        return redirect(url_for("admin.manage_feedback"))
    feedback.status = status
    db.session.commit()
    flash(f"Feedback marked as {status}.", "success")
    return redirect(request.referrer or url_for("admin.manage_feedback"))


@admin_bp.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
@login_required
def delete_feedback(feedback_id):
    feedback = db.get_or_404(Feedback, feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback entry removed.", "info")
    return redirect(url_for("admin.manage_feedback"))


@admin_bp.route("/events", methods=["GET", "POST"])
@login_required
def manage_events():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        date = request.form.get("date", "").strip()
        details = request.form.get("details", "").strip()
        image = request.files.get("image")
        image_filename = None
        if name and location and date:
            if image and image.filename:
                if not allowed_image(image.filename):
                    flash("Event image must be JPG, PNG, GIF, or WebP.", "error")
                    return redirect(url_for("admin.manage_events"))
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                image_filename = unique_upload_name(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], image_filename))
            event = Event(name=name, location=location, date=date, details=details, image_filename=image_filename)
            db.session.add(event)
            db.session.commit()
            flash("Event created successfully.", "success")
            return redirect(url_for("admin.manage_events"))
        flash("Name, location, and date are required.", "error")
    events = Event.query.order_by(Event.date).all()
    return render_template("admin/events.html", events=events)


@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    event = db.get_or_404(Event, event_id)
    if event.image_filename:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    for gallery_item in event.gallery_items:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], gallery_item.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(event)
    db.session.commit()
    flash("Event removed.", "info")
    return redirect(url_for("admin.manage_events"))


@admin_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        date = request.form.get("date", "").strip()
        details = request.form.get("details", "").strip()
        image = request.files.get("image")
        if name and location and date:
            if image and image.filename:
                if not allowed_image(image.filename):
                    flash("Event image must be JPG, PNG, GIF, or WebP.", "error")
                    return redirect(url_for("admin.edit_event", event_id=event.id))
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                new_filename = unique_upload_name(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename))
                if event.image_filename:
                    old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                event.image_filename = new_filename
            event.name = name
            event.location = location
            event.date = date
            event.details = details
            db.session.commit()
            flash("Event updated.", "success")
            return redirect(url_for("admin.manage_events"))
        flash("Name, location, and date are required.", "error")
    return render_template("admin/edit_event.html", event=event)


@admin_bp.route("/gallery", methods=["GET", "POST"])
@login_required
def manage_gallery():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        caption = request.form.get("caption", "").strip()
        event_id = request.form.get("event_id", type=int)
        images = [image for image in request.files.getlist("images") if image and image.filename]
        if not images:
            images = [image for image in request.files.getlist("image") if image and image.filename]
        event = db.session.get(Event, event_id) if event_id else None
        invalid_images = [image.filename for image in images if not allowed_image(image.filename)]
        if title and event and images and not invalid_images:
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            for index, image in enumerate(images, start=1):
                filename = unique_upload_name(image.filename)
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                image.save(file_path)
                item_title = title if len(images) == 1 else f"{title} {index}"
                gallery_item = GalleryItem(title=item_title, filename=filename, caption=caption, event_id=event.id)
                db.session.add(gallery_item)
            db.session.commit()
            photo_label = "photo" if len(images) == 1 else "photos"
            flash(f"{len(images)} event {photo_label} uploaded successfully.", "success")
            return redirect(url_for("admin.manage_gallery"))
        if invalid_images:
            flash("Every selected file must be a JPG, PNG, GIF, or WebP image.", "error")
        else:
            flash("Title, event, and at least one JPG, PNG, GIF, or WebP image are required.", "error")
    gallery_items = GalleryItem.query.order_by(GalleryItem.created_at.desc()).all()
    events = Event.query.order_by(Event.date).all()
    unassigned_gallery_items = [item for item in gallery_items if item.event_id is None]
    return render_template(
        "admin/gallery.html",
        gallery_items=gallery_items,
        events=events,
        unassigned_gallery_items=unassigned_gallery_items,
    )


@admin_bp.route("/gallery/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_gallery_item(item_id):
    item = db.get_or_404(GalleryItem, item_id)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], item.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(item)
    db.session.commit()
    flash("Gallery item removed.", "info")
    return redirect(url_for("admin.manage_gallery"))
