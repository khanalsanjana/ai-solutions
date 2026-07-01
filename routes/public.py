from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, Inquiry, Article, Feedback, GalleryItem, Event
from utils.forms import FeedbackForm, InquiryForm

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    featured_articles = Article.query.order_by(Article.published_at.desc()).limit(3).all()
    feedback_items = Feedback.query.filter_by(status="approved").order_by(Feedback.created_at.desc()).limit(3).all()
    gallery_items = GalleryItem.query.order_by(GalleryItem.created_at.desc()).limit(6).all()
    upcoming_events = Event.query.order_by(Event.date).limit(3).all()
    return render_template(
        "home.html",
        featured_articles=featured_articles,
        feedback_items=feedback_items,
        gallery_items=gallery_items,
        upcoming_events=upcoming_events,
    )


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/services")
def services():
    return render_template("services.html")


@public_bp.route("/solutions")
def solutions():
    return render_template("solutions.html")


@public_bp.route("/feedback", methods=["GET", "POST"])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback_item = Feedback(
            customer_name=form.customer_name.data,
            position=form.position.data,
            comment=form.comment.data,
            rating=form.rating.data,
            status="pending",
        )
        db.session.add(feedback_item)
        db.session.commit()
        flash("Thank you for sharing your feedback. It will appear after admin approval.", "success")
        return redirect(url_for("public.feedback"))
    feedback_items = Feedback.query.filter_by(status="approved").order_by(Feedback.created_at.desc()).all()
    return render_template("feedback.html", feedback_items=feedback_items, form=form)


@public_bp.route("/articles")
def articles():
    articles = Article.query.order_by(Article.published_at.desc()).all()
    return render_template("articles.html", articles=articles)


@public_bp.route("/articles/<int:article_id>")
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template("article_detail.html", article=article)


@public_bp.route("/gallery")
def gallery():
    events = Event.query.join(GalleryItem).distinct().order_by(Event.date).all()
    unassigned_gallery_items = GalleryItem.query.filter(GalleryItem.event_id.is_(None)).order_by(GalleryItem.created_at.desc()).all()
    total_gallery_items = sum(len(event.gallery_items) for event in events) + len(unassigned_gallery_items)
    return render_template(
        "gallery.html",
        events=events,
        unassigned_gallery_items=unassigned_gallery_items,
        total_gallery_items=total_gallery_items,
    )


@public_bp.route("/gallery/events/<int:event_id>")
def event_gallery(event_id):
    event = db.get_or_404(Event, event_id)
    gallery_items = GalleryItem.query.filter_by(event_id=event.id).order_by(GalleryItem.created_at.desc()).all()
    return render_template("event_gallery.html", event=event, gallery_items=gallery_items)


@public_bp.route("/events")
def events():
    events = Event.query.order_by(Event.date).all()
    return render_template("events.html", events=events)


@public_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    event = db.get_or_404(Event, event_id)
    gallery_items = GalleryItem.query.filter_by(event_id=event.id).order_by(GalleryItem.created_at.desc()).all()
    return render_template("event_detail.html", event=event, gallery_items=gallery_items)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            company=form.company.data,
            country=form.country.data,
            job_title=form.job_title.data,
            job_details=form.job_details.data,
        )
        try:
            db.session.add(inquiry)
            db.session.commit()
            flash("Your inquiry has been submitted successfully. We will contact you soon.", "success")
            return redirect(url_for("public.contact"))
        except Exception:
            db.session.rollback()
            flash("There was an issue saving the inquiry. Please try again.", "error")
    elif request.method == "POST":
        flash("Please correct the highlighted form errors before submitting.", "error")

    return render_template("contact.html", form=form)


@public_bp.route("/chatbot-response", methods=["POST"])
def chatbot_response():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").lower()
    answer = "I am here to help. Can you please clarify your question?"
    if "service" in message or "services" in message:
        answer = "AI-Solutions offers employee experience optimization, automation assistants, analytics dashboards, and integration services."
    elif "pricing" in message or "cost" in message:
        answer = "Pricing depends on project scope. Please submit an inquiry so our team can provide a tailored quote."
    elif "contact" in message or "support" in message:
        answer = "You can contact us through the Contact page or send an email to info@ai-solutions.example."
    elif "chatbot" in message or "faq" in message:
        answer = "This chatbot is a guided support helper. Ask about services, navigation, or inquiry submission."
    elif "event" in message or "webinar" in message:
        answer = "Visit the Events page to see upcoming webinars, launch meetups, and advisory sessions."
    elif "gallery" in message or "photo" in message:
        answer = "The Gallery page shows promotional event photos and examples of solution visuals."
    elif "about" in message:
        answer = "AI-Solutions creates AI-enabled digital employee experiences that improve productivity and satisfaction."
    elif "solution" in message or "project" in message:
        answer = "We build tailored AI solutions such as intelligent knowledge assistants, process automation, and analytics platforms."
    return jsonify({"reply": answer})
