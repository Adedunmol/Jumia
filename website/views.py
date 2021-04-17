from flask import Blueprint, render_template, request
from flask_login import login_required
from .models import Post, User

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, int)
    posts = Post.query.paginate(page=page, per_page=10)
    return render_template('home.html', posts=posts)


@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get(post_id)
    return render_template('post.html', post=post)
