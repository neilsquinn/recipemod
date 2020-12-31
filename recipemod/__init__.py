import os

from flask import Flask, url_for, redirect, render_template

from .auth import login_required
from .recipe import get_recipe

def create_app(test_config=None):
    app = Flask(__name__)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('No SECRET_KEY environment variable found')
    DATABASE = os.environ.get('DATABASE_URL')
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=DATABASE
        )
    
#   if test_config is None:
#       app.config.from_pyfile('config.py', silent=True)
#   else:
#       app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    from . import db
    db.init_app(app)
    
    from . import migrations
    app.cli.add_command(migrations.create_modifications_table_command)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    # from . import recipe
    # app.register_blueprint(recipe.bp)

    @app.route('/missing_image.jpg')
    def missing_image():
        return url_for('static', filename='logo.png')

    @app.route('/bookmarklet')
    def bookmarklet():
        return(render_template('extras/bookmarklet.html'))
    
    from . import api
    app.register_blueprint(api.bp)
    
    @app.route('/', defaults={'path': None})
    @app.route('/<path:path>')
    @login_required
    def serve_app(path):
        return render_template('index.html')
        # return url_for('static', filename='dist/index.html')
    return app
    