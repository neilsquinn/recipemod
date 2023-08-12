import click
from flask.cli import with_appcontext

from recipemod.db import get_db


def create_modifications_table():
    db = get_db()
    with db.cursor() as c:
        c.execute(
            """
DROP TABLE IF EXISTS modifications;
CREATE TABLE modifications (
    id SERIAL PRIMARY KEY,
    recipe_id integer REFERENCES recipes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed_fields jsonb,
    meta jsonb,
    created timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX modifications_recipe_id_idx ON modifications(recipe_id int4_ops);
"""
        )


@click.command("migrate-add-modifications-table")
@with_appcontext
def create_modifications_table_command():
    try:
        create_modifications_table()
    except Exception as e:
        click.echo(f"Failed: {e}")
    else:
        click.echo("Added modifications table")


def create_all_tables():
    with open("schema.sql") as infile:
        schema_sql = infile.read()
    db = get_db()
    with db.cursor() as c:
        c.execute(schema_sql)


@click.command("init-db")
@with_appcontext
def init_db():
    try:
        create_all_tables()
    except Exception as e:
        click.echo(f"Failed to initialize database: {e}")
    else:
        click.echo("Initialized database")
