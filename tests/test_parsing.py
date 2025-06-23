import json

import pytest

from recipemod.parsing import parse_recipe_html
from conftest import HTMLS_DIR, TARGET_JSONS_DIR


GOOD_RECIPES = [
    (open(HTMLS_DIR / f"{file.stem}.html").read(), json.load(file.open()))
    for file in TARGET_JSONS_DIR.glob("*.json")
]


@pytest.mark.parametrize("recipe_html,target_json", GOOD_RECIPES)
def test_parse_good(recipe_html, target_json):
    recipe = parse_recipe_html(recipe_html)
    recipe_dict = recipe.to_json()
    for key, target_val in target_json.items():
        assert target_val == recipe_dict[key], f"{key} should be the same"
