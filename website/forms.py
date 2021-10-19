from flask.app import Flask
from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User, Post
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_babel import lazy_gettext as _l


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=3)])
    email = StringField(_l('Email'), validators=[DataRequired(), validators.email()])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField(_l('Confirm_password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Please choose another username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Please choose another email.'))


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Login'))


class PostForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[DataRequired()])
    price = StringField(_l('Price'), validators=[DataRequired()])
    image = FileField(_l('Image'), validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Image only!')])
    submit = SubmitField(_l('Submit'))


class UpdateAccountForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), validators.email()])
    username = StringField(_l('Username'), validators=[DataRequired()])
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png'], 'Image only!')])
    submit = SubmitField(_l('Update Account'))


class UpdatePostForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    description = StringField(_l('Description'), validators=[DataRequired()])
    price = StringField(_l('Price'), validators=[DataRequired()])
    image = FileField(_l('Image'), validators=[FileAllowed(['jpg', 'png'], 'Image only!')])
    submit = SubmitField(_l('Update post'))


class EmailResetForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), validators.email()])
    submit = SubmitField(_l('Reset password'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError(_l('There is no user with this email. Kindly register.'))


class PasswordResetForm(FlaskForm):
    password = StringField(_l('Password'), validators=[DataRequired()])
    confirm_password = StringField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Reset password'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)