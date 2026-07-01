from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp


class InquiryForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(message="Please enter your full name."), Length(max=120)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Please enter your email."), Email(message="Enter a valid email address."), Length(max=120)],
    )
    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(message="Please enter your phone number."),
            Regexp(r"^[0-9+()\s-]{7,20}$", message="Phone number must contain only digits and symbols like + - ()."),
        ],
    )
    company = StringField(
        "Company Name",
        validators=[DataRequired(message="Please enter your company name."), Length(max=120)],
    )
    country = StringField(
        "Country",
        validators=[DataRequired(message="Please enter your country."), Length(max=80)],
    )
    job_title = StringField(
        "Job Title",
        validators=[DataRequired(message="Please enter your job title."), Length(max=120)],
    )
    job_details = TextAreaField(
        "Job Details",
        validators=[
            DataRequired(message="Please describe your project requirements."),
            Length(min=20, max=2000, message="Job details must be between 20 and 2000 characters."),
        ],
    )
    submit = SubmitField("Submit Inquiry")


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Username is required."), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(message="Password is required.")])
    captcha_answer = StringField(
        "CAPTCHA Answer",
        validators=[DataRequired(message="Please solve the CAPTCHA."), Regexp(r"^\d+$", message="CAPTCHA answer must be numeric.")],
    )
    submit = SubmitField("Sign In")


class FeedbackForm(FlaskForm):
    customer_name = StringField(
        "Your Name",
        validators=[DataRequired(message="Please enter your name."), Length(max=120)],
    )
    position = StringField("Job Title or Company", validators=[Optional(), Length(max=120)])
    comment = TextAreaField(
        "Feedback",
        validators=[DataRequired(message="Please enter your feedback."), Length(min=10, max=1000)],
    )
    rating = IntegerField(
        "Rating",
        validators=[DataRequired(message="Please select a rating."), NumberRange(min=1, max=5)],
    )
    submit = SubmitField("Submit Feedback")
