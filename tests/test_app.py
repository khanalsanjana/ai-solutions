from io import BytesIO

import pytest
from app import create_app
from models import db, Admin, Inquiry, Feedback, Event, GalleryItem


@pytest.fixture
def app(tmp_path):
    test_app = create_app(config_overrides={"UPLOAD_FOLDER": str(tmp_path)})
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with test_app.app_context():
        db.create_all()
        Admin.create_default_admin()
        yield test_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI-Solutions' in response.data


def test_contact_form_submission(client):
    response = client.post('/contact', data={
        'full_name': 'Student Tester',
        'email': 'student@test.com',
        'phone': '+442071234567',
        'company': 'University Labs',
        'country': 'UK',
        'job_title': 'Researcher',
        'job_details': 'I need an AI assistant for internal support.',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your inquiry has been submitted successfully' in response.data
    assert Inquiry.query.count() == 1


def test_admin_login_required(client):
    response = client.get('/admin/')
    assert response.status_code == 302
    assert '/admin/login' in response.headers['Location']


def test_public_feedback_requires_admin_approval(client):
    response = client.post('/feedback', data={
        'customer_name': 'Pending Reviewer',
        'position': 'Product Lead',
        'comment': 'This public comment should wait for approval.',
        'rating': '5',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'after admin approval' in response.data
    assert b'This public comment should wait for approval.' not in response.data

    feedback = Feedback.query.filter_by(customer_name='Pending Reviewer').one()
    assert feedback.status == 'pending'

    with client.session_transaction() as session:
        session['admin_authenticated'] = True
        session['admin_username'] = 'admin'

    response = client.post(f'/admin/feedback/{feedback.id}/status', data={'status': 'approved'}, follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Feedback, feedback.id).status == 'approved'

    response = client.get('/feedback')
    assert b'This public comment should wait for approval.' in response.data


def test_gallery_groups_photos_by_event(client):
    event = Event(name='Test Launch Event', location='Online', date='2026-09-10', details='Launch details')
    db.session.add(event)
    db.session.flush()
    db.session.add_all([GalleryItem(
        title='Launch Photo',
        filename='launch-photo.jpg',
        caption='Photo from the launch.',
        event_id=event.id,
    ), GalleryItem(
        title='Launch Photo Two',
        filename='launch-photo-two.jpg',
        caption='Second photo from the launch.',
        event_id=event.id,
    )])
    db.session.commit()

    response = client.get('/gallery')

    assert response.status_code == 200
    assert b'Test Launch Event' in response.data
    assert b'+1' in response.data
    assert b'Show more' in response.data
    assert b'Launch Photo Two' not in response.data

    response = client.get(f'/gallery/events/{event.id}')
    assert response.status_code == 200
    assert b'Test Launch Event' in response.data
    assert b'Launch Photo' in response.data
    assert b'Launch Photo Two' in response.data


def test_public_event_detail_shows_details_and_images(client):
    event = Event(
        name='Detail Event',
        location='Innovation Hall',
        date='2026-11-04',
        details='Detailed event description.',
        image_filename='cover.jpg',
    )
    db.session.add(event)
    db.session.flush()
    db.session.add(GalleryItem(
        title='Detail Event Photo',
        filename='detail-photo.jpg',
        caption='People attending the event.',
        event_id=event.id,
    ))
    db.session.commit()

    response = client.get('/events')
    assert response.status_code == 200
    assert f'/events/{event.id}'.encode() in response.data

    response = client.get(f'/events/{event.id}')
    assert response.status_code == 200
    assert b'Detail Event' in response.data
    assert b'Detailed event description.' in response.data
    assert b'cover.jpg' in response.data
    assert b'Detail Event Photo' in response.data
    assert b'detail-photo.jpg' in response.data


def test_admin_can_upload_multiple_gallery_photos_to_one_event(client):
    event = Event(name='Category A Event', location='Hall A', date='2026-10-01', details='Event details')
    db.session.add(event)
    db.session.commit()

    with client.session_transaction() as session:
        session['admin_authenticated'] = True
        session['admin_username'] = 'admin'

    response = client.post('/admin/gallery', data={
        'title': 'Category A Photo',
        'caption': 'Photos from category A.',
        'event_id': str(event.id),
        'images': [
            (BytesIO(b'first image'), 'first.jpg'),
            (BytesIO(b'second image'), 'second.png'),
        ],
    }, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'2 event photos uploaded successfully.' in response.data

    uploaded_items = GalleryItem.query.filter_by(event_id=event.id).order_by(GalleryItem.title).all()
    assert len(uploaded_items) == 2
    assert [item.title for item in uploaded_items] == ['Category A Photo 1', 'Category A Photo 2']

    response = client.get('/gallery')
    assert b'Category A Event' in response.data
    assert b'+1' in response.data

    response = client.get(f'/gallery/events/{event.id}')
    assert b'Category A Photo 1' in response.data
    assert b'Category A Photo 2' in response.data
