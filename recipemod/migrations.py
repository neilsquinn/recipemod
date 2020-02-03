import click
from flask.cli import with_appcontext

from recipemod.db import get_db


def create_modifications_table():
    db = get_db()
    with db.cursor() as c:
        c.execute('''
DROP TABLE IF EXISTS modifications;
CREATE TABLE modifications (
    id SERIAL PRIMARY KEY,
    recipe_id integer REFERENCES recipes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed_fields jsonb,
    meta jsonb,
    created timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX modifications_pkey ON modifications(id int4_ops);
CREATE INDEX modifications_recipe_id_idx ON modifications(recipe_id int4_ops);
''')

@click.command('migrate-add-modifications-table')
@with_appcontext
def create_modifications_table_command():
    try:
        create_modifications_table()
    except Exception as e:
        click.echo(f'Failed: {e}')
    else:
        click.echo('Added modifications table')
        
        
    
    