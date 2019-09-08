from flask import Blueprint, render_template
bp = Blueprint('extras', __name__)

@bp.route('/bookmarklet')
def bookmarklet():
    return(render_template('extras/bookmarklet.html'))