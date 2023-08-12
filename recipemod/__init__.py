import os
from logging.config import dictConfig

from flask import Flask, render_template
import werkzeug.exceptions

from .auth import login_required


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def create_app():
    app = Flask(__name__)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY environment variable found")
    DATABASE = os.environ.get("DATABASE_URL")
    app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE)

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

    @app.route("/bookmarklet")
    def bookmarklet():
        return render_template("extras/bookmarklet.html")

    from . import api

    app.register_blueprint(api.bp)

    @app.route("/", defaults={"path": None})
    @app.route("/<path:path>")
    @login_required
    def serve_app(path):
        return render_template("index.html")
        # return url_for('static', filename='dist/index.html')

    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def handle_server_error(error):
        return {"message": "Server encountered an unexpected error"}, 500

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(error):
        return {"message": "Bad request encountered"}, 400

    return app
