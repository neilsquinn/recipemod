from datetime import datetime
import urllib

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, flash
)
from werkzeug.exceptions import abort

from recipemod.auth import login_required
from recipemod.db import get_db
from recipemod.parsing import *

from psycopg2.extras import Json
import requests

bp = Blueprint('recipe', __name__)

def get_domain(url):
    return urllib.parse.urlsplit(url).netloc.replace('www.', '')

def save_recipe(db, url, user_agent):
    r = requests.get(url, headers={'User-Agent': user_agent})
    if not r:
        flash({'type': 'warning', 'text': f'Failed to load {url}'})
        print(f'Request to {url} failed with error {r.status_code}: \n {r.text} /nUser Agent: {r.request.headers["User-Agent"]}')
        return
    recipe_data = parse_recipe_html(r.text)
    if 'parse_error' in recipe_data:
        error_message = f'Unable to extract recipe from {url}'
        flash({'type': 'warning', 'text': error_message})
        print(error_message)
        return
    recipe_data['user_id'] = g.user['id']
    with db.cursor() as c:  
        for key, value in recipe_data.items():
            if type(value) in (list, dict):
                recipe_data[key] = Json(value)
        c.execute(
            'INSERT INTO recipes (name, description, yield, ingredients, '
            'instructions, times, user_id, image_url, url, authors, category, keywords)'
            'VALUES (%(name)s, %(description)s, %(yield)s, %(ingredients)s, '
            '%(instructions)s, %(times)s, %(user_id)s, %(image_url)s, '
            '%(url)s, %(authors)s, %(categories)s, %(keywords)s);', recipe_data
        )
        flash({'type': 'success', 'text': 'New recipe added.'})
    
@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    if request.method == 'POST':
        save = save_recipe(db, request.form['url'], request.headers['User-Agent'])
    with db.cursor() as c:
        c.execute(
        '''SELECT r.id, name, description, image_url, url, created
        FROM recipes r
        INNER JOIN users u ON u.id=r.user_id
        WHERE u.id=%s
        ORDER BY r.created DESC;''', (str(g.user['id']))
        )
        recipes = [dict(row) for row in c.fetchall()]
        for recipe in recipes:
            recipe['domain'] = get_domain(recipe['url'])
            if recipe['description']:
                if len(recipe['description']) > 150:
                    recipe['description'] = recipe['description'][:150] + '...'
            else:
                recipe['description'] = ''
    return render_template('recipe/index.html', recipes=recipes)

@bp.route('/add')
def add_recipe(index_request=None):
    db = get_db()
    save_recipe(db, request.args['url'], request.headers['User-Agent'])
    return redirect(url_for('recipe.index'))

def get_recipe(id, check_user=True):
    db = get_db()
    with db.cursor() as c:
        c.execute(
        'SELECT r.* '
        'FROM recipes r INNER JOIN users u on u.id=r.user_id '
        'WHERE r.id = %s', (id,)
        ) 
        recipe = c.fetchone()
    if not recipe:
        abort(404, f'Recipe {id} does not exist.')
    if check_user and recipe['user_id'] != g.user['id']:
        abort(403)  
    recipe = dict(recipe)
    recipe['domain'] = get_domain(recipe['url'])
    return recipe

@bp.route('/<int:id>/view')
@login_required
def view(id):
    recipe = get_recipe(id)
    return render_template('recipe/view.html', recipe=recipe)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    with db.cursor() as c:
        c.execute('DELETE FROM recipes WHERE id = %s;', (id,))
    return redirect(url_for('recipe.index'))

    
@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    def parse_form_lines(field):
        return  [line.strip() for line in request.form[field].split('\n')]

    recipe = get_recipe(id)
    if request.method == 'POST':
        ingredients = parse_form_lines('ingredients')
        instructions_type = recipe['instructions']['type']
        instructions = {'type': instructions_type}
        if instructions_type == 'steps':
            instructions['steps'] = parse_form_lines('instructions') 
        elif instructions_type == 'one_step':
            instructions['step'] = request.form['instructions']
        elif instructions_type == 'sections':
            sections = [{'name': section['name'], 'steps': parse_form_lines(f'instructions-{index}')}
                        for index, section in enumerate(recipe['instructions']['sections'], 1)]  
            instructions['sections'] = sections
        db = get_db()
        with db.cursor() as c:
            c.execute(
                'UPDATE recipes SET instructions = %(instructions)s, name = %(name)s, ' 
                'ingredients = %(ingredients)s, updated = %(updated)s '
                'WHERE id=%(id)s;', 
                {'ingredients': Json(ingredients), 'name': request.form['name'],
                'instructions': Json(instructions), 'id':id, 'updated': datetime.now()}
            )
        return redirect(url_for('recipe.view', id=id))
    
    
#     recipe['ingredients'] = '\n'.join(recipe['ingredients'])
    

    
    return render_template('recipe/edit.html', recipe=recipe)