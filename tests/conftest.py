from pathlib import Path

import pytest
import testing.postgresql
import psycopg2

from recipemod import create_app
from recipemod.db import get_db, init_db

data_sql_path = Path(__file__).parent / 'resources' / 'test_data.sql'
with data_sql_path.open() as infile:
	data_sql = infile.read()

@pytest.fixture
def app():
	with testing.postgresql.Postgresql() as postgresql:
		app = create_app(test_config={
			'TESTING': True,
			'DATABASE': postgresql.url()
		})
		with app.app_context():
			init_db()
			db = get_db()
			with db.cursor() as c:
				c.execute(data_sql)

		yield app
		
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()