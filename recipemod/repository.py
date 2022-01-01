from dataclasses import asdict
from datetime import datetime
from typing import List

from psycopg2.extras import Json

from recipemod.db import get_db
from recipemod.models import Recipe, Modification

from recipemod.db import get_db


def _row_to_recipe(row) -> Recipe:
    recipe = dict(row)
    for attr, col_name in [
        ("yield_", "yield"),
        ("categories", "category"),
    ]:
        if col_name in recipe:
            recipe[attr] = recipe.pop(col_name)

    for col_name in ["ratings", "video", "reviews", "cuisine"]:
        if col_name in recipe:
            del recipe[col_name]

    return Recipe(**recipe)


def get_recipe_detail(recipe_id: int, check_user=True) -> Recipe:
    db = get_db()
    with db.cursor() as c:
        c.execute(
            "SELECT r.* "
            "FROM recipes r INNER JOIN users u on u.id=r.user_id "
            "WHERE r.id = %s",
            (recipe_id,),
        )
        row = c.fetchone()
    if row:
        return _row_to_recipe(row)


def get_recipes_by_user(user_id: int) -> List[Recipe]:
    db = get_db()
    with db.cursor() as c:
        c.execute(
            "SELECT r.id, name, description, image_url, url, created "
            "FROM recipes r "
            "INNER JOIN users u ON u.id=r.user_id "
            "WHERE u.id=%s "
            "ORDER BY r.created DESC;",
            (str(user_id)),
        )
        return [_row_to_recipe(row) for row in c.fetchall()]


def save_recipe(recipe: Recipe) -> Recipe:
    db = get_db()
    payload = asdict(recipe)
    with db.cursor() as c:
        for key, value in payload.items():
            if type(value) in (list, dict):
                payload[key] = Json(value)
        c.execute(
            "INSERT INTO recipes (name, description, yield, ingredients, "
            "instructions, times, user_id, image_url, url, authors, category, keywords) "
            "VALUES (%(name)s, %(description)s, %(yield_)s, %(ingredients)s, "
            "%(instructions)s, %(times)s, %(user_id)s, %(image_url)s, "
            "%(url)s, %(authors)s, %(categories)s, %(keywords)s) RETURNING id;",
            payload,
        )
        recipe_id = c.fetchone()[0]
    return recipe_id


def delete_recipe(recipe_id: int) -> bool:
    db = get_db()
    with db.cursor() as c:
        c.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
        return True if c.rowcount > 0 else False
