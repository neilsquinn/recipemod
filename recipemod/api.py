import json
from datetime import datetime

from flask import Blueprint, g, current_app, request, abort
from flask.json import jsonify
import requests
from psycopg2.extras import Json

from recipemod.auth import login_required
from recipemod.db import get_db  # KILL
from recipemod.repository import (
    delete_recipe,
    get_recipe_detail,
    get_recipes_by_user,
    save_recipe,
)
from recipemod.models import Recipe
from recipemod.parsing import ParseError, parse_recipe_html

bp = Blueprint("api", __name__)


def _get_recipe(recipe_id, check_user=True) -> Recipe:
    recipe = get_recipe_detail(recipe_id)
    if not recipe:
        abort(404, f"Recipe {recipe_id} does not exist.")
    if check_user and recipe.user_id != g.user["id"]:
        abort(403)
    return recipe


@login_required
@bp.route("/api/recipes")
def recipes():
    """Get all recipes for this user."""
    recipes = get_recipes_by_user(g.user["id"])
    return {"recipes": [recipe.to_json() for recipe in recipes]}


@login_required
@bp.route("/api/recipes/add", methods=("POST",))
def add_recipe():
    data = json.loads(request.data.decode())
    url = data["url"]
    if not url:
        return { "error": "MISSING_URL", "msg": "No URL provided"}, 400

    resp = requests.get(url, headers={"User-Agent": request.headers["User-Agent"]})
    if not resp:
        return {"error": "REQUEST_FAILED", "msg": f"Request failed with error {resp.status_code}: \n {resp.text}"}, 500

    try:
        recipe = parse_recipe_html(resp.text)
    except (ParseError):
        return {"error": "PARSE_FAILED", "msg": "Unable to extract recipe data"}, 500

    if not recipe.url:
        recipe.url = url

    recipe.user_id = g.user["id"]
    recipe_id = save_recipe(recipe)
    recipe.id = recipe_id

    return {"recipe": recipe}


@login_required
@bp.route("/api/recipes/<int:recipe_id>")
def get_recipe_data(recipe_id):
    recipe = get_recipe_detail(recipe_id)
    if not recipe:
        abort(404, f"Recipe {recipe_id} does not exist.")
    return {"recipe": recipe.to_json()}


@login_required
@bp.route("/api/recipes/<int:recipe_id>", methods=("DELETE",))
def delete(recipe_id):
    status = delete_recipe(recipe_id)
    return "Recipe deleted" if status else ("Recipe not deleted", 500)


@login_required
@bp.route("/api/recipes/<int:recipe_id>", methods=("PUT",))
def update(recipe_id):
    new_recipe = json.loads(request.data.decode())["recipe"]
    old_recipe = _get_recipe(recipe_id)
    changed_fields = {
        key: old_recipe[key]
        for key in ["name", "ingredients", "instructions"]
        if new_recipe[key] != old_recipe[key]
    }
    print(changed_fields)
    if changed_fields:
        db = get_db()
        with db.cursor() as c:
            c.execute(
                "UPDATE recipes SET "
                "instructions = %(instructions)s, "
                "name = %(name)s, "
                "ingredients = %(ingredients)s, "
                "updated = %(updated)s "
                "WHERE id=%(id)s;",
                {
                    "ingredients": Json(new_recipe["ingredients"]),
                    "name": new_recipe["name"],
                    "instructions": Json(new_recipe["instructions"]),
                    "id": recipe_id,
                    "updated": datetime.now(),
                },
            )
            c.execute(
                """INSERT INTO modifications (recipe_id, changed_fields, meta) 
                VALUES (%(recipe_id)s,  %(changed_fields)s,  %(meta)s);""",
                {
                    "recipe_id": recipe_id,
                    "changed_fields": Json(changed_fields),
                    "meta": Json({}),
                },
            )

    return {"recipe": new_recipe}
