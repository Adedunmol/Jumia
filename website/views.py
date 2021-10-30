from flask import Blueprint, render_template, request, abort, redirect
from flask_login import login_required, current_user
from flask_socketio import emit, send, join_room, leave_room
import socketio
from stripe.api_resources import line_item, payment_method
from .models import Post, Room, User
import stripe
from . import socketio
from time import localtime, strftime

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

@views.route('/order/<product_id>', methods=['POST'])
def order(product_id):
    post = Post.query.get_or_404(product_id)
    if post is None:
        abort(404)
    checkout_session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'product_data': {
                    'name': post.title,
                },
                'unit_amount': post.price,
                'currency': 'usd',
            },
            'quantity': 1
        }],
        payment_method_types=['card'],
        mode='payment',
        success_url=request.host_url + 'order/success',
        cancel_url=request.host_url + 'order/cancel'
    )
    return redirect(checkout_session.url)

@views.route('/order/success')
def success():
    return render_template('success.html')

@views.route('/order/cancel')
def cancel():
    return render_template('cancel.html')

@views.route('/chat', methods=['GET', 'POST'])
def chat():
    new_rooms = Room.query.all()
    rooms = []
    for room in new_rooms:
        rooms.append(room.name)
    return render_template('chat.html', username=current_user.username, rooms=rooms)

@socketio.on('message')
def message(data):

    print(f"\n\n{data}\n\n")
    
    send({'msg': data['msg'], 'username': data['username'], 'timestamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])

@socketio.on('join')
def join(data):

    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('leave')
def leave(data):

    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])