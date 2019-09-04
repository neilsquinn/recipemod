import json
from datetime import timedelta
import re

import requests
from bs4 import BeautifulSoup
import ftfy

def clean_text(text):
    return ftfy.fix_text(BeautifulSoup(text, 'lxml').text.strip())


def parse_iso_8601(iso_duration) -> timedelta:
    time = iso_duration.split('T')[1]
    args = {}
    for char, arg in [('H', 'hours'), ('M', 'minutes'), ('S', 'seconds')]:
        if time:
            element = time.split(char)
            if len(element) > 1:
                args[arg] = float(element[0])
                time = element[1]
    return timedelta(**args)

def extract_ldjson(script_tags) -> list:
    def parse_tree(data, recipes):
        if type(data) == dict:
            if data.get('@type') == 'Recipe':
                recipes += [data]
            else:
                graph = data.get('@graph')
                if graph:
                    parse_tree(graph, recipes)
        elif type(data) == list:
            for item in data:
                parse_tree(item, recipes)
    
    recipes = []
    for tag in script_tags:
        parse_tree(json.loads(tag.text), recipes)
    
    if not recipes:
        return None
    elif len(recipes) > 1:
        raise ValueError('This page contains more than one recipe:',
                        [recipe['name'] for recipe in recipes])
    return recipes[0]

def ldjson_get_image_url(ldjson_recipe):
    image = ldjson_recipe.get('image')
    if type(image) == str:
        return image
    elif type(image) == list:
        return image[0]
    elif type(image) == dict and image['@type'] == 'ImageObject':
        return image['url']
    else:
        return None
    
def ldjson_get_instructions(ldjson_recipe):
    clean_text = lambda text: BeautifulSoup(text, 'lxml').text.strip()
    steps = ldjson_recipe.get('recipeInstructions')
    if steps:
        if type(steps) == str:
            return {'type':'one_step', 'step': clean_text(steps)}
        
        if type(steps) == dict and steps['@type'] == 'ItemList':
            steps = steps['itemListElement']
            
        if type(steps) == list:
            first_step = steps[0]
            if type(first_step) == str:
                return {'type': 'steps', 'steps': [clean_text(step) for step in steps]}
            elif type(first_step) == dict:
                print(first_step['@type'])
                if 'HowToStep' in first_step['@type']:
                    return {'type': 'steps', 'steps': [clean_text(step['text']) for step in steps]}
                elif 'HowToSection' in first_step['@type']:
                    sections = []
                    print('getting sections')
                    for section in steps:
                        first_substep = section['itemListElement'][0]
                        if type(first_substep) == list:
                            substeps = section['itemListElement']
                        elif type(first_substep) == dict and 'HowToStep' in first_substep['@type']:
                            substeps = [step['text'] for step in section['itemListElement']]
                        sections += [{'name': section['name'],
                                     'steps': [clean_text(step) for step in substeps]}]
                    return {'type': 'sections', 'sections': sections}
    else:    
        return {'type': None}

def ldjson_get_times(ldjson_recipe):
    times = {}
    for key, value in ldjson_recipe.items():
        if key.endswith('Time'):
            times[key.replace('Time', '')] = parse_iso_8601(value).seconds
    return times

def ldjson_get_author(ldjson_recipe):
    author = ldjson_recipe.get('author')
    if type(author) == str:
        return [author]
    elif type(author) == dict:
        return [author['name']]
    elif type(author) == list:
        return [item['name'] for item in author]

def save_recipe(url, browser_header):
    recipe = {}
    recipe['url'] = url
    r = requests.get(url, headers=browser_header)
    if not r:
        return {'request_error': r.status_code}
    
    soup = BeautifulSoup(r.text, 'lxml')
    ldjson_recipe = extract_ldjson(soup.find_all('script', type='application/ld+json'))
    if ldjson_recipe:
        recipe['name'] = ldjson_recipe.get('name')
        description = ldjson_recipe.get('description')
        if description:
            description = clean_text(description)
        recipe['description'] = description
        recipe['yield'] = ldjson_recipe.get('recipeYield')
        recipe['image_url'] = ldjson_get_image_url(ldjson_recipe)
        recipe['instructions'] = ldjson_get_instructions(ldjson_recipe)
        recipe['times'] = ldjson_get_times(ldjson_recipe)
        recipe['authors'] = ldjson_get_author(ldjson_recipe)
        recipe['ingredients'] = [clean_text(item) for item in ldjson_recipe.get('recipeIngredient')]
        
        return recipe
    
    recipe_tags = soup.find(itemtype=re.compile("https?://schema.org/Recipe"))
    if recipe_tags:

        recipe['name'] = recipe_tags.find(itemprop=['name']).text
        description_tag = recipe_tags.find(itemprop='description')
        if not description_tag:
            text = None 
        elif 'content' in description_tag.attrs:
            text = description_tag.get['content']
        else:
            text=description_tag.text
        recipe['description'] = text
        
        instructions_tags = recipe_tags.find_all(itemprop='recipeInstructions')
        if len(instructions_tags) == 1:
            instructions = [line.strip() for line in instructions_tags[0].text.split('\n')]
        elif len(instructions_tags) > 1:
            instructions = [tag.text.strip().replace('\r', '') 
                            for tag in instructions_tags]
        else:
            instructions = []
        recipe['instructions'] = {'steps': instructions, 'type': 'steps'}
        recipe['authors'] = [tag.text for tag in recipe_tags.find_all(itemprop='author')]
        
        ingredients_tags = recipe_tags.find_all(itemprop='recipeIngredient')
        if not len(ingredients_tags):
            ingredients_tags = recipe_tags.find_all(itemprop='ingredients')
        recipe['ingredients'] = [tag.text.strip() for tag in ingredients_tags]
        
        times = {}
        for tag in recipe_tags.find_all(re.compile('\w*Time')):
            times[key.replace('Time', '')] = parse_iso_8601(tag['content']).seconds
        recipe['times'] = times
        recipe_yield = recipe_tags.find(itemprop='recipeYield')
        if recipe_yield:
            recipe['yield'] = recipe_yield.text
        else:
            recipe['yield'] = None
        
        image_tag = recipe_tags.find(itemprop='thumbnailUrl')
        image_url = None
        if image_tag:
            if 'content' in image_tag.attrs:
                image_url = image_tag['content']
            else:
                image_url = image_tag['src']
        else:
            image_tag = recipe_tags.find('img')
            if image_tag:
                image_url = image_tag['src']
        recipe['image_url'] = image_url
        return recipe
        
    else:
        return {'parse_error': 'no recipe JSON found'} # todo look for tags