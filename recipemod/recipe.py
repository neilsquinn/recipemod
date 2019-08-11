from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from recipemod.auth import login_required
from recipemod.db import get_db

bp = Blueprint('recipe', __name__)

@bp.route('/')
def index():
    db = get_db()
    with db.cursor() as c:
        c.execute('''SELECT r.id, name, description, created, updated, yield, ingredients, times, category, cuisine, keywords, ratings, video, reviews 
                     FROM recipes r
                     INNER JOIN users u ON u.id=r.author
                     WHERE u.id=%s;''', (str(g.user['id'])))
        recipes = c.fetchall()
        return render_template('recipe/index.html', recipes=recipes)

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        url = request.form('link')
    db = get_db()
    with db.cursor() as c:
        pass

@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    pass