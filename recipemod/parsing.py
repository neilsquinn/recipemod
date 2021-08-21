import json
from datetime import timedelta
import re
import urllib

from bs4 import BeautifulSoup, NavigableString
from ftfy import fix_text

from recipemod.models import Recipe

newline_regex = r"(\s*(\r|\n)\s*)+"


class ParseError(Exception):
    pass


def clean_text(text, remove_newlines=False) -> str:
    cleaned = fix_text(BeautifulSoup(text, "lxml").text.strip())
    if remove_newlines:
        cleaned = re.sub(newline_regex, " ", cleaned)
    return cleaned


def parse_iso_8601(iso_duration) -> timedelta:
    time = iso_duration.split("T")[1]
    args = {}
    for char, arg in [("H", "hours"), ("M", "minutes"), ("S", "seconds")]:
        if time:
            element = time.split(char)
            if len(element) > 1:
                args[arg] = float(element[0])
                time = element[1]
    return timedelta(**args)


def complete_url(image_url, page_url):
    image_url_components = urllib.parse.urlparse(image_url)
    if not image_url_components.netloc:
        page_url_components = urllib.parse.urlparse(page_url)
        return urllib.parse.urlunparse(
            page_url_components[:2] + image_url_components[2:]
        )
    else:
        return image_url


class MicrodataParser:
    def __init__(self, tag):
        self.tag = tag

    @staticmethod
    def get_attr_text(tag, attr=None):
        """Parse a tag to get the content of the meta tag, or some other attr,
        or the text"""
        if tag.name == "meta":
            if "content" in tag.attrs:
                return tag.attrs["content"]
            elif "value" in tag.attrs:
                return tag.attrs["value"]
        elif attr and attr in tag.attrs:
            return tag.attrs[attr]
        else:
            return tag.text

    def find_props(self, prop_name, verbose=False):
        """Recursively parse webpages to find correct tag in Microdata
        version of schema.org recipes."""

        def digger(prop_name, tag, relevant_tags):
            for child in tag.find_all(recursive=False):
                if verbose:
                    print(child.name, child.attrs, len(child.contents))
                item_prop = child.attrs.get("itemprop")
                if prop_name == item_prop:
                    relevant_tags += [child]
                if "itemscope" in child.attrs:
                    if verbose:
                        print("skipping itemscope")
                    continue
                if child.contents:
                    digger(prop_name, child, relevant_tags)
            return relevant_tags

        return digger(prop_name, self.tag, [])

    def extract_text_props(self, prop_name, single_result=False, clean=True):
        tags = self.find_props(prop_name)
        texts = [
            " ".join([token.strip() for token in self.get_attr_text(tag).split()])
            for tag in tags
        ]
        if clean:
            texts = [fix_text(text) for text in texts]
        if single_result:
            if texts:
                if len(texts) > 1:
                    print(f"Found {tags}, returning{tags[0]}")
                return texts[0]
            else:
                print(f"No tags found for {prop_name}")
                return None
        return texts

    def get_times(self):
        times = {}
        for prop_name in ("cook", "prep", "total"):
            time_tags = self.find_props(f"{prop_name}Time")
            if time_tags:
                time_string = self.get_attr_text(time_tags[0], "datetime")
                if time_string and time_string.startswith("P"):
                    times[prop_name] = parse_iso_8601(time_string).seconds
        return times

    def get_image(self):
        image_tags = self.find_props("image")
        if image_tags:
            return self.get_attr_text(image_tags[0], attr="src")

    def get_instructions(self):
        instructions_tags = self.find_props("recipeInstructions")
        instructions = []
        for instructions_tag in instructions_tags:
            if instructions_tag.name in ("li", "p"):
                step = [re.sub(newline_regex, " ", instructions_tag.text.strip())]
            else:
                step = [
                    fix_text(tag.text.strip())
                    for tag in instructions_tag.find_all("li")
                    if not isinstance(tag, NavigableString)
                    and not tag.findChildren("li")
                ]
            instructions += step

        return {"steps": instructions, "type": "steps"}

    def get_ingredients(self):
        ingredients = self.extract_text_props("recipeIngredient")
        if not ingredients:
            ingredients = self.extract_text_props("ingredients")
        return ingredients

    def get_authors(self):
        authors = self.extract_text_props("author")
        if not authors:
            author_tags = self.find_props("author")
            authors = [author_tag.text.strip() for author_tag in author_tags]
        return authors

    def get_recipe(self):
        # recipe = {}
        # recipe["url"] = self.extract_text_props("url", single_result=True)
        # recipe["name"] = self.extract_text_props("name", single_result=True)
        # recipe["description"] = self.extract_text_props(
        #     "description", single_result=True
        # )
        # recipe["authors"] = self.get_authors()
        # recipe["image_url"] = self.get_image()
        # recipe["instructions"] = self.get_instructions()
        # recipe["ingredients"] = self.get_ingredients()
        # recipe["times"] = self.get_times()
        # recipe["yield"] = self.extract_text_props("recipeYield", single_result=True)
        # recipe["categories"] = self.extract_text_props("recipeCategory")
        # recipe["keywords"] = self.extract_text_props("keywords")

        # return recipe

        return Recipe(
            name=self.extract_text_props("name", single_result=True),
            description=self.extract_text_props("description", single_result=True),
            url=self.extract_text_props("url", single_result=True),
            authors=self.get_authors(),
            image_url=self.get_image(),
            instructions=self.get_instructions(),
            ingredients=self.get_ingredients(),
            times=self.get_times(),
            yield_=self.extract_text_props("recipeYield", single_result=True),
            categories=self.extract_text_props("recipeCategory"),
            keywords=self.extract_text_props("keywords"),
        )


class LDJSONParser:
    def __init__(self, script_tags):
        self.script_tags = script_tags

    def extract_ldjson_recipe(self) -> list:
        def parse_tree(data, recipes):
            if type(data) == dict:
                if data.get("@type") == "Recipe":
                    recipes += [data]
                elif data.get("mainEntity"):
                    recipes += [data["mainEntity"]]
                else:
                    graph = data.get("@graph")
                    if graph:
                        parse_tree(graph, recipes)
            elif type(data) == list:
                for item in data:
                    parse_tree(item, recipes)

        recipes = []
        for tag in self.script_tags:
            parse_tree(json.loads(tag.string), recipes)

        if not recipes:
            return None
        elif len(recipes) > 1:
            raise ValueError(
                "This page contains more than one recipe:",
                [recipe["name"] for recipe in recipes],
            )
        return recipes[0]

    @staticmethod
    def get_image_url(ldjson_recipe) -> str:
        image = ldjson_recipe.get("image")
        if type(image) == list:
            image = image[0]
        if type(image) == str:
            return image
        if type(image) == dict and image["@type"] == "ImageObject":
            return image["url"]

    @staticmethod
    def get_instructions(ldjson_recipe) -> dict:
        steps = ldjson_recipe.get("recipeInstructions")
        if steps:
            if type(steps) == str:
                return {"type": "one_step", "step": clean_text(steps)}

            if type(steps) == dict and steps["@type"] == "ItemList":
                steps = steps["itemListElement"]

            if type(steps) == list:
                first_step = steps[0]
                if type(first_step) == str:
                    return {
                        "type": "steps",
                        "steps": [
                            clean_text(step, remove_newlines=True) for step in steps
                        ],
                    }
                elif type(first_step) == dict:
                    if "HowToStep" in first_step["@type"]:
                        return {
                            "type": "steps",
                            "steps": [
                                clean_text(step["text"], remove_newlines=True)
                                for step in steps
                            ],
                        }
                    elif "HowToSection" in first_step["@type"]:
                        sections = []
                        for section in steps:
                            first_substep = section["itemListElement"][0]
                            if type(first_substep) == list:
                                substeps = section["itemListElement"]
                            elif (
                                type(first_substep) == dict
                                and "HowToStep" in first_substep["@type"]
                            ):
                                substeps = [
                                    step["text"] for step in section["itemListElement"]
                                ]
                            sections += [
                                {
                                    "name": section["name"],
                                    "steps": [
                                        clean_text(step, remove_newlines=True)
                                        for step in substeps
                                    ],
                                }
                            ]
                        return {"type": "sections", "sections": sections}
        else:
            return {"type": None}

    @staticmethod
    def get_times(ldjson_recipe) -> dict:
        times = {}
        for key, value in ldjson_recipe.items():
            if key.endswith("Time") and value:
                try:
                    times[key.replace("Time", "")] = parse_iso_8601(value).seconds
                except (IndexError):
                    continue
        return times

    @staticmethod
    def get_authors(ldjson_recipe) -> list:
        author = ldjson_recipe.get("author")
        if type(author) == str:
            return [author]
        elif type(author) == dict:
            return [author["name"]]
        elif type(author) == list:
            return [item["name"] for item in author if item["name"]]

    @staticmethod
    def get_keywords(ldjson_recipe) -> list:
        keywords = ldjson_recipe.get("keywords")
        if keywords:
            if type(keywords) == str:
                return [keyword.strip() for keyword in keywords.split(",") if keyword]
            return keywords

    @staticmethod
    def get_categories(ldjson_recipe) -> list:
        categories = ldjson_recipe.get("recipeCategories")
        if not categories:
            categories = ldjson_recipe.get("recipeCategory")
        if type(categories) == str:
            return [categories]
        elif type(categories) == list:
            return categories

    def get_recipe(self):
        ldjson_recipe = self.extract_ldjson_recipe()
        if not ldjson_recipe:
            return
        # recipe = {}
        # recipe["url"] = ldjson_recipe.get("url")
        # recipe["name"] = clean_text(ldjson_recipe.get("name"))
        # description = ldjson_recipe.get("description")
        # recipe["description"] = clean_text(description) if description else None
        # recipe["yield"] = ldjson_recipe.get("recipeYield")
        # recipe["image_url"] = self.get_image_url(ldjson_recipe)
        # recipe["instructions"] = self.get_instructions(ldjson_recipe)
        # recipe["times"] = self.get_times(ldjson_recipe)
        # recipe["authors"] = self.get_authors(ldjson_recipe)
        # recipe["ingredients"] = [
        #     clean_text(item) for item in ldjson_recipe.get("recipeIngredient")
        # ]
        # recipe["keywords"] = self.get_keywords(ldjson_recipe)
        # recipe["categories"] = self.get_categories(ldjson_recipe)

        # return recipe

        description = ldjson_recipe.get("description")
        return Recipe(
            name=clean_text(ldjson_recipe.get("name")),
            description=clean_text(description) if description else None,
            url=ldjson_recipe.get("url"),
            image_url=self.get_image_url(ldjson_recipe),
            yield_=ldjson_recipe.get("recipeYield"),
            instructions=self.get_instructions(ldjson_recipe),
            ingredients=[
                clean_text(item) for item in ldjson_recipe.get("recipeIngredient")
            ],
            times=self.get_times(ldjson_recipe),
            authors=self.get_authors(ldjson_recipe),
            keywords=self.get_keywords(ldjson_recipe),
            categories=self.get_categories(ldjson_recipe),
        )


def parse_recipe_html(html: str, verbose: bool = False) -> Recipe:
    soup = BeautifulSoup(html, "lxml")

    ldjson_tags = soup.find_all("script", type="application/ld+json")
    if ldjson_tags:
        parser = LDJSONParser(ldjson_tags)
        recipe = parser.get_recipe()
        if recipe:
            if verbose:
                print("LD+JSON recipe found")
            return recipe

    recipe_microdata_elem = soup.find(itemtype=re.compile("https?://schema.org/Recipe"))
    if recipe_microdata_elem:
        if verbose:
            print("Recipe microdata element found")
        parser = MicrodataParser(recipe_microdata_elem)
        return parser.get_recipe()

    raise ParseError("No parsable recipe could be found.")
