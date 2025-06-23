from flask.testing import FlaskClient
import pytest
import requests

from recipemod.models import DBRecipe, Recipe
from recipemod.repository import get_user_by_name, save_recipe
from conftest import HTMLS_DIR


@pytest.fixture()
def test_user(client: FlaskClient):
    resp = client.post("/auth/register", data={"username": "test", "password": "test"})
    assert resp
    client.post("/auth/login", data={"username": "test", "password": "test"})


class SuccessRecipeResponse:
    def __bool__(self):
        return True

    @property
    def text(self):
        html = open(
            HTMLS_DIR / "classic_french_aligot_recipe_-_the_spruce_eats.html"
        ).read()
        return html

    @property
    def status_code(self):
        return 200


def test_add_recipe(test_user, client, monkeypatch):

    def mock_get(*args, **kwargs):
        return SuccessRecipeResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    data = {"url": "https://example.com/recipe"}
    response = client.post("/api/recipes/add", json=data)
    assert response.status_code == 200
    assert "recipe" in response.json
    assert response.json["recipe"]["name"] == "Classic French Aligot"


def test_get_recipes(test_user, client):
    # Add some recipes to the DB for the test user
    with client.application.app_context():
        user = get_user_by_name("test")

        recipe1 = Recipe(
            name="Recipe 1",
            description="This is recipe 1",
            image_url="https://example.com/recipe1.jpg",
            url="https://example.com/recipe1",
        )
        recipe2 = Recipe(
            name="Recipe 2",
            description="This is recipe 2",
            image_url="https://example.com/recipe2.jpg",
            url="https://example.com/recipe2",
        )
        recipe3 = Recipe(
            name="Recipe 3",
            description="This is recipe 3",
            image_url="https://example.com/recipe3.jpg",
            url="https://example.com/recipe3",
        )

        save_recipe(recipe1, user.id)
        save_recipe(recipe2, user.id)
        save_recipe(recipe3, user.id)

    # Get the recipes for the test user
    response = client.get("/api/recipes")
    assert response.status_code == 200
    recipes = response.json["recipes"]

    # Check that we got the recipes back
    assert len(recipes) == 3
    assert recipes[0]["name"] == "Recipe 3"
    assert recipes[1]["name"] == "Recipe 2"
    assert recipes[2]["name"] == "Recipe 1"


def test_delete_recipe(test_user, client):
    # Add a recipe to the DB for the test user
    with client.application.app_context():
        user = get_user_by_name("test")

        recipe = Recipe(
            name="Recipe 1",
            description="This is recipe 1",
            image_url="https://example.com/recipe1.jpg",
            url="https://example.com/recipe1",
        )
        saved_recipe = save_recipe(recipe, user.id)

    # Delete the recipe
    response = client.delete(f"/api/recipes/{saved_recipe.id}")
    assert response.status_code == 200
    assert response.json["msg"] == "Recipe deleted"

    # Check that the recipe is no longer in the list of all recipes
    response = client.get("/api/recipes")
    assert response.status_code == 200
    recipes = response.json["recipes"]
    assert saved_recipe.id not in [recipe["id"] for recipe in recipes]


def test_delete_recipe_not_found(test_user, client):
    # Try to delete a recipe that does not exist
    response = client.delete("/api/recipes/999")
    assert response.status_code == 404
    assert response.json["msg"] == "Unable to delete recipe with ID 999 as not found."
