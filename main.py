import socketio
from werkzeug import debug
from website import create_app, db
from search import add_to_index, remove_from_index, query_index
from website.models import Post, Room
from flask_migrate import Migrate
from website import cli
import os
import click

app = create_app()
Migrate(app, db)

@app.shell_context_processor
def inject_functions():
    return dict(db=db, add_to_index=add_to_index, remove_from_index=remove_from_index, query_index=query_index, Post=Post, app=app, Room=Room)


@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d website/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d website/translations'):
        raise RuntimeError('compile command failed')

@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d website/translations -l' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')

if __name__ == '__main__':
    socketio.run(app, debug=True)