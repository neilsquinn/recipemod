from dataclasses import asdict
from datetime import datetime
import logging

from psycopg2.extras import Json, DictCursor
import psycopg2.errors

from recipemod.db import get_db
from recipemod.models import DBRecipe, Recipe, Modification, User

from recipemod.db import get_db

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Generic repository error"""


class NotFoundError(RepositoryError):
    """Item not found in database"""


def get_user_by_id(user_id: int) -> User:
    logger.debug("Fetching user with id %i", user_id)
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as c:
        try:
            c.execute(
                "SELECT id, username, password FROM users WHERE id = %s;", (user_id,)
            )
            user = c.fetchone()
            if user is None:
                logger.exception("Unable to find user with id %s", user_id)
                raise NotFoundError(f"Unable to find user with id {user_id}")
            return User(**user)
        except psycopg2.errors.Error:
            logger.exception("Error getting user with id %i", user_id)
            raise


def get_user_by_name(username: str) -> User:
    logger.debug("Fetching user with name %s", username)
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as c:
        try:
            c.execute(
                "SELECT id, username, password FROM users WHERE username = %s;",
                (username,),
            )
            user = c.fetchone()
            if user is None:
                logger.exception("Unable to find user with name %s", username)
                raise NotFoundError(f"Unable to find user with name {username}")
            return User(**user)
        except psycopg2.errors.Error:
            logger.exception("Error getting user with id %i", username)
            raise


def _row_to_recipe(row) -> DBRecipe:
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

    return DBRecipe(**recipe)


def get_recipe_detail(recipe_id: int) -> DBRecipe:
    logger.debug("Fetching recipe detail for ID %s", recipe_id)
    db = get_db()
    with db.cursor() as c:
        try:
            c.execute(
                "SELECT r.* "
                "FROM recipes r INNER JOIN users u on u.id=r.user_id "
                "WHERE r.id = %s",
                (recipe_id,),
            )
            row = c.fetchone()
            if row:
                return _row_to_recipe(row)
            logger.error("Unable to load recipe with ID %s as not found", recipe_id)
            raise NotFoundError(
                f"Unable to delete recipe with ID {recipe_id} as not found"
            )
        except psycopg2.errors.Error:
            logger.exception("Error getting detail from recipe %s", recipe_id)
            raise


def get_recipes_by_user(user_id: int) -> list[DBRecipe]:
    logger.debug("Fetching recipes for user %s", user_id)
    db = get_db()
    with db.cursor() as c:
        try:
            logger.debug("Fetching recipes for user %s", user_id)
            c.execute(
                "SELECT r.id, name, description, image_url, url, created "
                "FROM recipes r "
                "INNER JOIN users u ON u.id=r.user_id "
                "WHERE u.id=%s "
                "ORDER BY r.created DESC;",
                (str(user_id)),
            )
            return [_row_to_recipe(row) for row in c.fetchall()]
        except psycopg2.errors.Error:
            logger.exception("Error getting recipes for user %s", user_id)
            raise


def save_recipe(recipe: Recipe, user_id: int) -> DBRecipe:
    """Save recipe to database"""
    payload = asdict(recipe)
    for key, value in payload.items():
        if type(value) in (list, dict):
            payload[key] = Json(value)
    payload["user_id"] = user_id

    db = get_db()
    with db.cursor() as c:
        try:
            c.execute(
                "INSERT INTO recipes (name, description, yield, ingredients, "
                "instructions, times, user_id, image_url, url, authors, category, keywords) "
                "VALUES (%(name)s, %(description)s, %(yield_)s, %(ingredients)s, "
                "%(instructions)s, %(times)s, %(user_id)s, %(image_url)s, "
                "%(url)s, %(authors)s, %(categories)s, %(keywords)s) RETURNING *;",
                payload,
            )
        except psycopg2.errors.Error:
            logger.exception("Error writing recipe '%s' to database: '%s'", recipe.url)
            raise
        created_recipe = c.fetchone()
    db_recipe = _row_to_recipe(created_recipe)
    return db_recipe


def delete_recipe(recipe_id: int) -> None:
    db = get_db()
    with db.cursor() as c:
        try:
            c.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
            if not c.rowcount > 0:
                logger.error("Deletion of recipe with id %s found no rows", recipe_id)
                raise NotFoundError(
                    f"Unable to delete recipe with ID {recipe_id} as not found"
                )
        except psycopg2.errors.Error:
            logger.exception(
                "Error deleting recipe with ID %s from database", recipe_id
            )
            raise


def update_recipe(recipe: DBRecipe):
    db = get_db()
    with db.cursor() as c:
        try:
            c.execute(
                "UPDATE recipes SET "
                "instructions = %(instructions)s, "
                "name = %(name)s, "
                "ingredients = %(ingredients)s, "
                "updated = %(updated)s "
                "WHERE id=%(id)s;",
                {
                    "ingredients": Json(recipe.ingredients),
                    "name": recipe.name,
                    "instructions": Json(recipe.instructions),
                    "id": recipe.id,
                    "updated": datetime.now(),
                },
            )
        except psycopg2.errors.Error:
            logger.exception("Error updating recipe with ID %s in database", recipe.id)
            raise


def save_modification(mod: Modification):
    db = get_db()
    with db.cursor() as c:
        try:
            c.execute(
                """INSERT INTO modifications (recipe_id, changed_fields, meta) 
                VALUES (%(recipe_id)s,  %(changed_fields)s,  %(meta)s);""",
                {
                    "recipe_id": mod.recipe_id,
                    "changed_fields": Json(mod.changed_fields),
                    "meta": Json({}),
                },
            )
        except psycopg2.errors.Error:
            logger.exception(
                "Error saving modification to recipe with ID %s and changed fields %s",
                mod.recipe_id,
                mod.changed_fields,
            )
            raise
