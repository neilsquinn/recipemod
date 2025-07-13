import json

import pytest

from recipemod.parsing import parse_recipe_html
from conftest import HTMLS_DIR, TARGET_JSONS_DIR


GOOD_RECIPES = [file.stem for file in TARGET_JSONS_DIR.glob("*.json")]


@pytest.mark.parametrize("recipe_name", GOOD_RECIPES)
def test_parse_good(recipe_name):
    html_file = HTMLS_DIR / f"{recipe_name}.html"
    json_file = TARGET_JSONS_DIR / f"{recipe_name}.json"

    with open(html_file, "r") as f:
        recipe_html = f.read()

    with open(json_file, "r") as f:
        target_json = json.load(f)

    recipe = parse_recipe_html(recipe_html)
    recipe_dict = recipe.to_json()
    for key, target_val in target_json.items():
        assert target_val == recipe_dict[key], f"{key} should be the same"
