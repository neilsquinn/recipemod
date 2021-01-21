import os
from pathlib import Path

from flask import Flask, url_for, redirect, render_template

from .auth import login_required

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="development",
        DATABASE="postgresql://localhost:5432/recipemod",
    )

    if test_config:
        app.config.update(test_config)
    else:
        app.config.update({
            key: os.environ.get(key) 
            for key in ['SECRET_KEY', 'DATABASE']
        })
    print(app.config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        
    from . import db
    db.init_app(app)
    
    from . import migrations
    app.cli.add_command(migrations.create_modifications_table_command)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
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
    