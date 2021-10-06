from website import create_app, db
from search import add_to_index, remove_from_index, query_index
from website.models import Post
from flask_migrate import Migrate

app = create_app()
Migrate(app, db)

@app.shell_context_processor
def inject_functions():
    return dict(db=db, add_to_index=add_to_index, remove_from_index=remove_from_index, query_index=query_index, Post=Post, app=app)

if __name__ == '__main__':
    app.run(debug=True)
