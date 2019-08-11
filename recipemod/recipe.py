from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from recipemod.auth import login_required
from recipemod.db import get_db
from recipemod.parsing import *

from psycopg2.extras import Json

bp = Blueprint('recipe', __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    with db.cursor() as c:
        if request.method == 'POST':
            url = request.form['url']
            recipe_data = get_recipe(url, {'User-Agent': request.headers['User-Agent']})
            recipe_data['user_id'] = g.user['id']
            for key, value in recipe_data.items():
                if type(value) in (list, dict):
                    recipe_data[key] = Json(value)
#             breakpoint()
            c.execute(
                '''INSERT INTO recipes (name, description, yield, ingredients, instructions, times, user_id) 
                VALUES (%(name)s, %(description)s, %(yield)s, %(ingredients)s, %(instructions)s, %(times)s, %(user_id)s);''',
                recipe_data)
            db.commit()
            return redirect(url_for('recipe.index'))
        
        
        c.execute('''SELECT r.id, name, description, created, updated, yield, ingredients, times, category, cuisine, keywords, ratings, video, reviews 
                     FROM recipes r
                     INNER JOIN users u ON u.id=r.user_id
                     WHERE u.id=%s;''', (str(g.user['id'])))
        recipes = c.fetchall()
        return render_template('recipe/index.html', recipes=recipes)


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    pass