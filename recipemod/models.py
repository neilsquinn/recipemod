from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Union


@dataclass
class Recipe:
    id: int = None
    name: str = None
    user_id: int = None
    description: str = None
    url: str = None
    image_url: str = None
    authors: List[str] = None
    instructions: Dict[str, Any] = None
    ingredients: List[str] = None
    times: Dict[str, int] = None
    yield_: Union[List[str], int] = None
    categories: List[str] = None
    keywords: List[str] = None
    created: str = None  # for now
    updated: str = None

    def to_json(self):
        return {
            **asdict(self),
            "yield": self.yield_,
        }


@dataclass
class Modification:
    id: int
    recipe_id: int
    changed_fields: Dict[str, Any]
    meta: Dict[str, Any]
    created: datetime
