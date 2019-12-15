import json
from datetime import timedelta
import re

from bs4 import BeautifulSoup
import ftfy

def clean_text(text) -> str:
    return ftfy.fix_text(BeautifulSoup(text, 'lxml').text.strip())

class MicrodataParser:
    def __init__(self, tag):
        self.tag = tag
    
    def find_props(self, prop_name, verbose=False):
        '''Recursively parse webpages to find correct tag in Microdata 
#     version of schema.org recipes.'''

        def digger(prop_name, tag, relevant_tags): 
            for child in tag.find_all(recursive=False): 
                if verbose:
                    print(child.name, child.attrs, len(child.contents)) 
                if 'itemscope' in child.attrs: 
                    if verbose:
                        print('skipping itemscope') 
                    continue 
                item_prop = child.attrs.get('itemprop') 
                if prop_name == item_prop: 
                    relevant_tags += [child] 
                if child.contents: 
                    digger(prop_name, child, relevant_tags) 
            return relevant_tags 
        return digger(prop_name, self.tag, []) 
        
    def extract_text_props(self, prop_name, single_result=False, clean=True):
        tags = self.find_props(prop_name)
        texts = [tag.attrs['content'] if tag.name == 'meta' else tag.text 
                 for tag in tags]
        if clean:
            texts = [clean_text(text) for text in texts]
        if single_result:
            if texts:
                if len(texts) > 1:
                    print(f'Found {tags}, returning{tags[0]}')
                return texts[0]
            else:
                print('No tags found')
                return None
        return texts

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
            elif data.get('mainEntity'):
                recipes += [data['mainEntity']]
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

def ldjson_get_image_url(ldjson_recipe) -> str:
    image = ldjson_recipe.get('image')
    if type(image) == list:
        image = image[0]
    if type(image) == str:
        return image
    if type(image) == dict and image['@type'] == 'ImageObject':
        return image['url']
    
def ldjson_get_instructions(ldjson_recipe) -> dict:
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
                if 'HowToStep' in first_step['@type']:
                    return {'type': 'steps', 'steps': [clean_text(step['text']) for step in steps]}
                elif 'HowToSection' in first_step['@type']:
                    sections = []
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

def ldjson_get_times(ldjson_recipe) -> dict:
    times = {}
    for key, value in ldjson_recipe.items():
        if key.endswith('Time') and value:
            times[key.replace('Time', '')] = parse_iso_8601(value).seconds
    return times

def ldjson_get_author(ldjson_recipe) -> list:
    author = ldjson_recipe.get('author')
    if type(author) == str:
        return [author]
    elif type(author) == dict:
        return [author['name']]
    elif type(author) == list:
        return [item['name'] for item in author]

def ldjson_get_keywords(ldjson_recipe) -> list:
    keywords = ldjson_recipe.get('keywords')
    if keywords:
        return keywords.split(',')

def ldjson_get_categories(ldjson_recipe) -> list:
    categories = ldjson_recipe.get('recipeCategories')
    if type(categories) == str:
        return [categories]
    elif type(categories) == list:
        return categories

def microdata_get_times(mdparser):
    times = {}
    for prop_name in ('cook', 'prep', 'total'):
        time_tags = mdparser.find_props(f'{prop_name}Time')
        if time_tags:
            times[prop_name] = parse_iso_8601(time_tags[0].attrs['datetime']).seconds
    return times
    
def microdata_get_image(mdparser):
    image_tags = mdparser.find_props('image')
    if image_tags:
        return image_tags[0].attrs['src']

def microdata_get_instructions(mdparser):
    instructions_tags = mdparser.find_props('recipeInstructions')
    instructions = [
        clean_text(tag.text) 
        for tag in instructions_tags[0].find_all(recursive=False)
        ]
    return {'steps': instructions, 'type': 'steps'}

def parse_recipe_html(html) -> dict:
    recipe = {}
    soup = BeautifulSoup(html, 'lxml')
    canonical_tag = soup.find('link', rel='canonical')
    if canonical_tag:
        recipe['url'] = canonical_tag['href']
    else:
        recipe['url'] = url
    
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
        recipe['keywords'] = ldjson_get_keywords(ldjson_recipe)
        recipe['categories'] = ldjson_get_categories(ldjson_recipe)
        
        return recipe
    
    recipe_tag = soup.find(itemtype=re.compile("https?://schema.org/Recipe"))
    if recipe_tag:
        mdparser = MicrodataParser(recipe_tag)
        recipe['name'] = mdparser.extract_text_props('name', single_result=True)
        recipe['description'] = mdparser.extract_text_props('description', single_result=True)
        recipe['authors'] = mdparser.extract_text_props('author')
        recipe['image_url'] = microdata_get_image(mdparser)
        recipe['instructions'] = microdata_get_instructions(mdparser)
        recipe['ingredients'] = mdparser.extract_text_props('recipeIngredient')
        recipe['times'] = microdata_get_times(mdparser)
        recipe['yield'] = mdparser.extract_text_props('recipeYield', single_result=True)
        recipe['categories'] = mdparser.extract_text_props('recipeCategory')
        recipe['keywords'] = mdparser.extract_text_props('keywords')
        
        return recipe
        
    else:
        recipe['url']
        image_url_meta = soup.head.find('meta', attrs={'itemprop': 'image'})
        if image_url_meta:
            recipe['image_url'] = image_url_meta.attrs['content']
        
        recipe['parse_error'] = 'no recipe metadata found'
        return recipe # todo look for tags