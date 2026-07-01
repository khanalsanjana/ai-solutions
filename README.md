# AI-Solutions

Responsive company website and admin management system built with Flask for an academic product development project.

## Project Summary
AI-Solutions is a professional landing site for an AI consulting startup. The public website includes marketing pages, customer inquiry submission, and a simple rule-based chatbot. The admin panel secures access with form-based CAPTCHA and manages inquiries, articles, feedback, events, and gallery assets.

## Folder Structure
```
/
├── app.py
├── config.py
├── models/
├── routes/
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
├── database/
├── services/
├── utils/
├── tests/
├── requirements.txt
└── README.md
```

## Setup Instructions
1. Create a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open `http://127.0.0.1:5000/`

## Admin Access
- Username: `admin`
- Password: `Password123!`

## Academic Documentation
The project includes:
- Requirement mapping
- Database models for admin, inquiry, gallery, feedback, article, and event
- Use case and architecture description
- Functional and authentication test cases
- Deployment notes for local and cloud hosting

## Notes
This implementation focuses on modular Flask architecture, secure admin authentication, server-side validation, and responsive Tailwind-based layout.
