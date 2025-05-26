from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email
from wtforms import PasswordField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed

class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    content = TextAreaField('Comment', validators=[DataRequired()])
    parent_id = HiddenField()
    submit = SubmitField('Post Comment')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class AdminRegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo('password', message='Passwords must match.')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ArticleSubmissionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    document = FileField('Supporting Document', validators=[FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')])
    submit = SubmitField('Submit')
