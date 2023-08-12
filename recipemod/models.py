from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Union, Optional

JSONDict = Dict[str, Any]


@dataclass
class Recipe:
    id: int | None = None
    name: str | None = None
    user_id: int | None = None
    description: str | None = None
    url: str | None = None
    image_url: str | None = None
    authors: List[str] | None = None
    instructions: JSONDict | None = None
    ingredients: List[str] | None = None
    times: JSONDict | None = None
    yield_: Union[List[str], int] | None = None
    categories: List[str] | None = None
    keywords: List[str] | None = None
    created: str | None = None  # for now
    updated: str | None = None

    def to_json(self):
        return {
            **asdict(self),
            "yield": self.yield_,
        }

    @classmethod
    def from_json(cls, data: JSONDict) -> "Recipe":
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
