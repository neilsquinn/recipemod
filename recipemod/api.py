from flask import (
    Blueprint, g, current_app, request, abort
)
from flask.json import jsonify
import requests
from psycopg2.extras import Json
import json

from recipemod.auth import login_required
from recipemod.db import get_db
from recipemod.parsing import parse_recipe_html
from recipemod.recipe import get_recipe

bp = Blueprint('api', __name__)

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

        return jsonify(recipes)

@login_required  
@bp.route('/api/recipes/add', methods=('POST',))
def add_recipe():
    print('AHHHHHHHHHHH!!!!!!!')
    data = json.loads(request.data.decode())
    url = data['url']
    if not url:
        abort (400, 'Error: no URL provided')

    r = requests.get(url, headers={'User-Agent': request.headers["User-Agent"]})
    if not r:
        return (f'Error: Request to {url} failed with error {r.status_code}: \n {r.text}', 500)
    
    recipe_data = parse_recipe_html(r.text)
    if 'parse_error' in recipe_data:
        about (500, f'Error: Unable to extract recipe from {url}')
    
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
    return jsonify(recipe)

@login_required
@bp.route('/api/recipes/<int:recipe_id>/')
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
    return jsonify(recipe)

@login_required
@bp.route('/api/recipes/<int:recipe_id>/delete', methods=('DELETE',))
def delete(recipe_id):
    db = get_db()
    with db.cursor() as c:
        c.execute('DELETE FROM recipes WHERE id = %s;', (recipe_id,))
    return "Success"