from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Union, Optional

JSONDict = Dict[str, Any]


@dataclass
class User:
    id: int
    username: str
    password: str


@dataclass(kw_only=True)
class Recipe:
    name: str
    description: str | None = None
    url: str | None = None
    image_url: str | None = None
    authors: list[str] | None = None
    instructions: JSONDict | None = None
    ingredients: list[str] | None = None
    times: JSONDict | None = None
    yield_: Union[list[str], int] | None = None
    categories: list[str] | None = None
    keywords: list[str] | None = None

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["yield"] = data.pop("yield_")
        return data


@dataclass
class DBRecipe(Recipe):
    id: int
    created: str
    user_id: int | None = None
    updated: str | None = None

    @classmethod
    def from_json(cls, data: JSONDict) -> "DBRecipe":
        data = {"yield_" if k == "yield" else k: v for k, v in data.items()}
        return cls(**data)


@dataclass
class Modification:
    recipe_id: int
    changed_fields: JSONDict
    meta: Optional[JSONDict] = None
    id: Optional[int] = None
    created: Optional[datetime] = None

    @classmethod
    def from_recipes(cls, old_recipe: Recipe, new_recipe: Recipe) -> "Modification":
        changed_fields = {
            key: getattr(old_recipe, key)
            for key in ["name", "ingredients", "instructions"]
            if getattr(new_recipe, key) != getattr(old_recipe, key)
        }
        return cls(changed_fields=changed_fields, recipe_id=old_recipe.id)
