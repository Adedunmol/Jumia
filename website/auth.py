from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, g
from flask.globals import current_app
from flask_login import current_user, login_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, PostForm, UpdateAccountForm, UpdatePostForm, EmailResetForm, PasswordResetForm, SearchForm
from . import db, bcrypt, mail
from .models import User, Post
import os
import secrets
from PIL import Image
from flask_mail import Message
from flask_babel import _

auth = Blueprint('auth', __name__)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

@auth.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('views.home'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('auth.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('auth.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url) 

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(_('Your account has been created!'), category='success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            flash(_('You are logged in successfully'), category='success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('views.home'))
        else:
            flash(_('The details you entered is not correct'), category='danger')
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))


def save_image(img):
    f_name = secrets.token_hex(8)
    _, pic_ext = os.path.splitext(img.filename)
    picture_fn = f_name + pic_ext
    picture_path = os.path.join(auth.root_path, 'static/image', picture_fn)

    output_size = (150, 150)
    i = Image.open(img)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@auth.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        image = form.image.data
        image_file = save_image(image)
        post = Post(title=form.title.data, description=form.description.data,
                     price=form.price.data, image_file=image_file, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your product has been posted'), category='success')
        return redirect(url_for('views.home'))
    return render_template('new_post.html', form=form)


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image.data:
            image = save_image(form.image.data)
            current_user.image_file = image
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        flash(_('Your account has been updated'), category='success')
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    image = url_for('static', filename='image/' + current_user.image_file)
    return render_template('account.html', form=form, image=image)


@auth.route('/user/<username>', methods=['GET', 'POST'])
def user_posts(username):
    page = request.args.get('page', 1, int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).paginate(page=page, per_page=10)
    return render_template('user_posts.html', posts=posts, user=user)


@auth.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = UpdatePostForm()
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        if form.image.data:
            image = save_image(form.image.data)
            post.image = image
        post.title = form.title.data
        post.description = form.description.data
        post.price = form.price.data
        db.session.commit()
        flash(_('Your product has been posted'), category='success')
        return redirect(url_for('views.home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.price.data = post.price
    return render_template('update_post.html', form=form, post=post)


@auth.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(_('Your product has been deleted.'), category='success')
    return redirect(url_for('views.home'))


def send_mail(user):
    token = user.get_reset_token()
    message = Message('Password Reset Request', sender='noreply@gmail.com', recipients=[user.email])
    message.body = f''' To reset your password visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}
If you did not make this request please ignore and no changes will be made
'''
    mail.send(message)


@auth.route('/reset_email', methods=['GET', 'POST'])
def reset_email():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = EmailResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_mail(user)
        flash(_('A link has been sent to your email'), category='success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_email.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = PasswordResetForm()
    user = User.verify_reset_token(token)
    if user is None:
        flash(_('This token is invalid or expired'), category='info')
        return redirect(url_for('auth.reset_mail'))
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(_('Your password has been updated. You can now log in.'), category='success')
        return redirect(url_for('auth.login'))
    return render_template('password_reset.html', form=form)
