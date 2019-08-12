from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from recipemod.auth import login_required
from recipemod.db import get_db
from recipemod.parsing import *

from psycopg2.extras import Json
import urllib

bp = Blueprint('recipe', __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    with db.cursor() as c:
        if request.method == 'POST':
            url = request.form['url']
            recipe_data = save_recipe(url, {'User-Agent': request.headers['User-Agent']})
            recipe_data['user_id'] = g.user['id']
            for key, value in recipe_data.items():
                if type(value) in (list, dict):
                    recipe_data[key] = Json(value)
#             breakpoint()
            c.execute(
                '''INSERT INTO recipes (name, description, yield, ingredients, instructions, times, user_id, image_url, url) 
                VALUES (%(name)s, %(description)s, %(yield)s, %(ingredients)s, %(instructions)s, %(times)s, %(user_id)s, %(image_url)s, %(url)s);''',
                recipe_data
            )
            db.commit()
            return redirect(url_for('recipe.index'))
        
        c.execute(
        '''SELECT r.id, name, description, image_url, url, created
        FROM recipes r
        INNER JOIN users u ON u.id=r.user_id
        WHERE u.id=%s
        ORDER BY r.created DESC;''', (str(g.user['id']))
        )
        recipes = [dict(row) for row in c.fetchall()]
        for recipe in recipes:
            recipe['domain'] = urllib.parse.urlsplit(recipe['url']).netloc.replace('www.', '')
            if recipe['description']:
                if len(recipe['description']) > 150:
                    recipe['description'] = recipe['description'][:150] + '...'
            else:
                recipe['description'] = ''
        
        return render_template('recipe/index.html', recipes=recipes)

def get_recipe(id, check_user=True):
    db = get_db()
    with db.cursor() as c:
        c.execute(
        '''SELECT r.id, name, description, created, updated, yield, ingredients, instructions, times, category, cuisine, keywords, ratings, video, reviews, user_id, image_url, url
        FROM recipes r INNER JOIN users u on u.id=r.user_id
        WHERE r.id = %s''', (id,)
        ) 
        recipe = c.fetchone()
    if not recipe:
        abort(404, f'Recipe {id} does not exist.')
    if check_user and recipe['user_id'] != g.user['id']:
        abort(403)  
    print(recipe.keys)
    return recipe

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_recipe(id)
    db = get_db()
    with db.cursor() as c:
        c.execute('DELETE FROM recipes WHERE id = %s;', (id,))
    db.commit()
    return redirect(url_for('recipe.index'))

@bp.route('/<int:id>')
@login_required
def view(id):
    recipe = get_recipe(id, check_user=True)
    return render_template('recipe/view.html', recipe=recipe)
    
@bp.route('/<int:id>/edit')
@login_required
def edit(id):
    pass