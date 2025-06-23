from datetime import datetime
import os
from pathlib import Path

from flask import Flask
from flask.testing import FlaskClient
import psycopg2
import pytest

from recipemod import create_app
from recipemod.db import init_db


def _create_test_db(db_name: str):
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="",
    )
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {db_name}")
    cur.close()


def _remove_test_db(db_name: str):
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="",
    )
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE {db_name}")
    cur.close()


@pytest.fixture()
def app():
    print("trying to app")
    test_db_name = f"recipemod_test_{datetime.now().strftime('%y%m%d_%H%M%S')}"
    os.environ.update(
        {
            "DATABASE_URL": f"postgresql://@localhost:5432/{test_db_name}",
            "SECRET_KEY": "fsdfsdfsdf",
        },
    )

    _create_test_db(test_db_name)
    app = create_app()
    with app.app_context():
        init_db()

    yield app
    print("removing db")

    _remove_test_db(test_db_name)


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


HTMLS_DIR = Path(__file__).parent / "recipe_htmls"
TARGET_JSONS_DIR = Path(__file__).parent / "target_jsons"
