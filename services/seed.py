from datetime import UTC, datetime
from models import db, Admin, Article, Event, Feedback, GalleryItem


def initialize_sample_data():
    Admin.create_default_admin()

    if Article.query.count() == 0:
        sample_articles = [
            Article(
                title="Enhancing Digital Employee Experience with AI",
                summary="How AI automation improves employee satisfaction and productivity.",
                content="AI-driven tools can streamline workflows, reduce manual tasks, and personalize internal communication.",
                published_at=datetime.now(UTC),
            ),
            Article(
                title="Intelligent Enterprise Search for Faster Outcomes",
                summary="Designing search experiences that help teams find answers quickly.",
                content="A robust enterprise search solution indexes documents across systems and offers contextual relevance.",
                published_at=datetime.now(UTC),
            ),
        ]
        db.session.bulk_save_objects(sample_articles)

    if Feedback.query.count() == 0:
        sample_feedback = [
            Feedback(customer_name="Aisha Carter", position="HR Director", comment="AI-Solutions transformed our onboarding experience with conversational workflows.", rating=5, status="approved"),
            Feedback(customer_name="Felix Martin", position="Operations Head", comment="The automation platform reduced ticket volume and improved employee satisfaction.", rating=4, status="approved"),
        ]
        db.session.bulk_save_objects(sample_feedback)

    if Event.query.count() == 0:
        sample_events = [
            Event(name="AI Employee Experience Webinar", location="Online", date="2026-07-15", details="A live session exploring digital employee journey improvements."),
            Event(name="Product Launch Meetup", location="Downtown Conference Center", date="2026-08-01", details="Networking event and demo of our latest AI assistant."),
        ]
        db.session.add_all(sample_events)
        db.session.flush()

    if GalleryItem.query.count() == 0:
        events = Event.query.order_by(Event.date).all()
        sample_gallery = [
            GalleryItem(
                title="AI Dashboard",
                filename="dashboard-sample.jpg",
                caption="Interactive analytics for HR teams.",
                event_id=events[0].id if events else None,
            ),
            GalleryItem(
                title="Chatbot Interface",
                filename="chatbot-sample.jpg",
                caption="Responsive chatbot for employee support.",
                event_id=events[1].id if len(events) > 1 else (events[0].id if events else None),
            ),
        ]
        db.session.bulk_save_objects(sample_gallery)

    db.session.commit()
