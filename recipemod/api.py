import json
from datetime import datetime

from flask import (
    Blueprint, g, current_app, request, abort
)
from flask.json import jsonify
import requests
from psycopg2.extras import Json

from recipemod.auth import login_required
from recipemod.db import get_db
from recipemod.parsing import parse_recipe_html

bp = Blueprint('api', __name__)

def get_recipe(recipe_id, check_user=True):
    db = get_db()
    with db.cursor() as c:
        c.execute(
        'SELECT r.* '
        'FROM recipes r INNER JOIN users u on u.id=r.user_id '
        'WHERE r.id = %s', (recipe_id,)
        ) 
        recipe = c.fetchone()
    if not recipe:
        abort(404, f'Recipe {recipe_id} does not exist.')
    if check_user and recipe['user_id'] != g.user['id']:
        abort(403)  
    recipe = dict(recipe)
    return recipe

@login_required
@bp.route('/api/recipes')
def recipes():
    '''Get all recipes for this user.'''
    db = get_db()
    with db.cursor() as c:
        c.execute(
        'SELECT r.id, name, description, image_url, url, created '
        'FROM recipes r '
        'INNER JOIN users u ON u.id=r.user_id '
        'WHERE u.id=%s '
        'ORDER BY r.created DESC;', (str(g.user['id']))
        )
        recipes = [dict(row) for row in c.fetchall()]

        return {'recipes': recipes}

@login_required  
@bp.route('/api/recipes/add', methods=('POST',))
def add_recipe():
    data = json.loads(request.data.decode())
    url = data['url']
    if not url:
        abort(400, 'Error: no URL provided')

    resp = requests.get(url, headers={'User-Agent': request.headers["User-Agent"]})
    if not resp:
        return (f'Error: Request to {url} failed with error {r.status_code}: \n {resp.text}', 500)
    recipe_data = parse_recipe_html(resp.text)
    print(recipe_data)
    if 'parse_error' in recipe_data:
        return {'error': 'Unable to extract recipe data'}
    
    if not recipe_data.get('url'):
        recipe_data['url'] = url
    
    recipe_data['user_id'] = g.user['id']
    
    db = get_db()
    with db.cursor() as c:  
        for key, value in recipe_data.items():
            if type(value) in (list, dict):
                recipe_data[key] = Json(value)
        c.execute(
            'INSERT INTO recipes (name, description, yield, ingredients, '
            'instructions, times, user_id, image_url, url, authors, category, keywords) '
            'VALUES (%(name)s, %(description)s, %(yield)s, %(ingredients)s, '
            '%(instructions)s, %(times)s, %(user_id)s, %(image_url)s, '
            '%(url)s, %(authors)s, %(categories)s, %(keywords)s) RETURNING id;', 
            recipe_data
        )
        recipe_id = c.fetchone()[0]
    recipe = get_recipe(recipe_id)
    return {'recipe': recipe}

@login_required
@bp.route('/api/recipes/<int:recipe_id>')
def get_recipe_data(recipe_id):
    print('ooo')
    db = get_db()
    with db.cursor() as c:
        c.execute(
        'SELECT r.* '
        'FROM recipes r INNER JOIN users u on u.id=r.user_id '
        'WHERE r.id = %s', (recipe_id,)
        ) 
        recipe = c.fetchone()
    if not recipe:
        abort(404, f'Recipe {recipe_id} does not exist.')
    recipe = dict(recipe)
    return {'recipe': recipe}

@login_required
@bp.route('/api/recipes/<int:recipe_id>', methods=('DELETE',))
def delete(recipe_id):
    db = get_db()
    with db.cursor() as c:
        c.execute('DELETE FROM recipes WHERE id = %s;', (recipe_id,))
    return "Success"

@login_required
@bp.route('/api/recipes/<int:recipe_id>', methods=('PUT',))
def update(recipe_id):
    new_recipe = json.loads(request.data.decode())['recipe']
    old_recipe = get_recipe(recipe_id)
    changed_fields = {
        key: old_recipe[key] 
        for key in ['name', 'ingredients', 'instructions']
        if new_recipe[key] != old_recipe[key]
    }
    print(changed_fields)
    if changed_fields:
        db = get_db()
        with db.cursor() as c:
            c.execute(
                'UPDATE recipes SET '
                'instructions = %(instructions)s, '
                'name = %(name)s, '
                'ingredients = %(ingredients)s, '
                'updated = %(updated)s '
                'WHERE id=%(id)s;',
                {
                    'ingredients': Json(new_recipe['ingredients']), 
                    'name': new_recipe['name'],
                    'instructions': Json(new_recipe['instructions']), 
                    'id': recipe_id, 
                    'updated': datetime.now()
                }
            )
            c.execute(
                '''INSERT INTO modifications (recipe_id, changed_fields, meta) 
                VALUES (%(recipe_id)s,  %(changed_fields)s,  %(meta)s);''', 
                {
                'recipe_id': recipe_id, 
                'changed_fields': Json(changed_fields),
                'meta': Json({})
            })

    return {'recipe': new_recipe}
