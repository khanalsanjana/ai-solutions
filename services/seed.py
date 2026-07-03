from datetime import UTC, datetime
from models import db, Admin, Article, Event, Feedback, GalleryItem, Inquiry


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
            Feedback(customer_name="Sanjana Khanal", position="Project Coordinator", comment="The website management system is clear, fast, and easy to update from the admin panel.", rating=5, status="approved"),
            Feedback(customer_name="Kreety Pandey", position="Content Manager", comment="Uploading event details and reviewing customer messages is simple and well organized.", rating=5, status="approved"),
            Feedback(customer_name="Priyanka Bhandari", position="Business Analyst", comment="The contact and feedback sections help us respond to visitors quickly and professionally.", rating=4, status="approved"),
            Feedback(customer_name="Sandesh Khanal", position="Operations Lead", comment="The gallery and event pages make our public updates look polished and trustworthy.", rating=5, status="approved"),
        ]
        db.session.bulk_save_objects(sample_feedback)

    if Event.query.count() == 0:
        sample_events = [
            Event(name="Team Planning Workshop", location="Butwal", date="2026-07-15", details="Sanjana Khanal and Kreety Pandey will coordinate a workshop on project planning, content updates, and admin workflows."),
            Event(name="Customer Feedback Review", location="Kathmandu", date="2026-08-01", details="Priyanka Bhandari and Sandesh Khanal will review customer feedback, contact inquiries, and website improvement priorities."),
            Event(name="Gallery Content Session", location="Pokhara", date="2026-08-20", details="Aayushma Dumre, Puja Marasini, and Hemanta Tharu will prepare event photos and gallery captions for publication."),
        ]
        db.session.add_all(sample_events)
        db.session.flush()

    if Inquiry.query.count() == 0:
        sample_inquiries = [
            Inquiry(
                full_name="Laxman Magarati",
                email="laxman.magarati@example.com",
                phone="+9779801001001",
                company="Butwal Creative Group",
                country="Nepal",
                job_title="Marketing Officer",
                job_details="I would like to discuss a website update package for event listings, gallery content, and customer inquiry management.",
            ),
            Inquiry(
                full_name="Krishna Khanal",
                email="krishna.khanal@example.com",
                phone="+9779801001002",
                company="Khanal Business Services",
                country="Nepal",
                job_title="Business Owner",
                job_details="Please contact me about improving our contact form, feedback review process, and admin dashboard workflow.",
            ),
            Inquiry(
                full_name="Aayush Pandey",
                email="aayush.pandey@example.com",
                phone="+9779801001003",
                company="Pandey Digital Studio",
                country="Nepal",
                job_title="Web Designer",
                job_details="I need support organizing client event photos and publishing gallery albums with clean captions and event details.",
            ),
        ]
        db.session.bulk_save_objects(sample_inquiries)

    if GalleryItem.query.count() == 0:
        events = Event.query.order_by(Event.date).all()
        sample_gallery = [
            GalleryItem(
                title="Workshop Planning",
                filename="dashboard-sample.jpg",
                caption="Sanjana Khanal presenting the project update plan.",
                event_id=events[0].id if events else None,
            ),
            GalleryItem(
                title="Feedback Review",
                filename="chatbot-sample.jpg",
                caption="Kreety Pandey and Priyanka Bhandari reviewing customer responses.",
                event_id=events[1].id if len(events) > 1 else (events[0].id if events else None),
            ),
        ]
        db.session.bulk_save_objects(sample_gallery)

    db.session.commit()
