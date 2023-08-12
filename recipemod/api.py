from enum import Enum
import json
import logging

from flask import Blueprint, g, request
import requests

from recipemod.auth import login_required
from recipemod import repository, parsing
from recipemod.models import Modification, Recipe

bp = Blueprint("api", __name__)

logger = logging.getLogger(__name__)


class Error(Enum):
    NOT_FOUND = "NOT_FOUND"
    REQUEST_FAILED = "REQUEST_FAILED"
    MISSING_URL = "MISSING_URL"
    PARSE_FAILED = "PARSE_FAILED"


@login_required
@bp.get("/api/recipes")
def recipes():
    """Get all recipes for this user."""
    recipes = repository.get_recipes_by_user(g.user["id"])
    return {"recipes": [recipe.to_json() for recipe in recipes]}


@login_required
@bp.post("/api/recipes/add")
def add_recipe():
    data = json.loads(request.data.decode())
    url = data["url"]
    if not url:
        return {"error": Error.MISSING_URL.value, "msg": "No URL provided"}, 400

    resp = requests.get(url, headers={"User-Agent": request.headers["User-Agent"]})
    if not resp:
        logger.info("Request to URL '%s' failed with status %s", url, resp.status_code)
        return {
            "error": Error.REQUEST_FAILED.value,
            "msg": f"Request failed with error {resp.status_code}: \n {resp.text}",
        }, 500

    try:
        recipe = parsing.parse_recipe_html(resp.text)
    except parsing.ParseError as error:
        logger.error(
            "Error parsing recipe data from URL '%s', message: '%s'", url, error
        )
        return {
            "error": Error.PARSE_FAILED.value,
            "msg": "Unable to extract recipe data",
        }, 500

    if not recipe.url:
        recipe.url = url

    recipe.user_id = g.user["id"]
    recipe = repository.save_recipe(recipe)

    logger.info(
        "Saved recipe from URL '%s' with name '%s' as %d for user ID %s ",
        url,
        recipe.name,
        recipe.id,
        recipe.user_id,
    )
    return {"recipe": recipe}


@login_required
@bp.get("/api/recipes/<int:recipe_id>")
def get_recipe_data(recipe_id):
    recipe = repository.get_recipe_detail(recipe_id)
    if not recipe:
        logger.error(
            "Unable to load recipe ID %s for user ID %s as it does not exist",
            recipe_id,
            g.user["id"],
        )
        return {
            "error": Error.NOT_FOUND.value,
            "msg": f"Recipe {recipe_id} does not exist.",
        }, 404
    return {"recipe": recipe.to_json()}


@login_required
@bp.delete("/api/recipes/<int:recipe_id>")
def delete(recipe_id):
    try:
        repository.delete_recipe(recipe_id)
    except repository.NotFoundError:
        logger.exception("Unable to delete recipe with ID %s as not found", recipe_id)
        return {
            "msg": f"Unable to delete recipe with ID {recipe_id} as not found.",
            "error": Error.NOT_FOUND.value,
        }, 404

    logger.info("Deleted recipe with ID %s", recipe_id)

    return {"msg": "Recipe deleted"}


@login_required
@bp.put("/api/recipes/<int:recipe_id>")
def update(recipe_id):
    recipe = Recipe.from_json(json.loads(request.data.decode())["recipe"])
    try:
        old_recipe = repository.get_recipe_detail(recipe_id)
    except repository.NotFoundError:
        return {
            "msg": f"Unable to modify recipe with ID {recipe_id} as not found.",
            "error": Error.NOT_FOUND.value,
        }, 404
    mod = Modification.from_recipes(old_recipe, recipe)

    if mod.changed_fields:
        logger.info("Updating recipe ID %s with changes: %s", recipe.id, mod)
        repository.update_recipe(recipe)
        repository.save_modification(mod)
    else:
        logger.info(
            "Received request to update recipe ID %s but no changes found", recipe.id
        )

    return {"recipe": recipe}
