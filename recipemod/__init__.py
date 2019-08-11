import os

from flask import Flask

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='amanda',
		DATABASE='recipemod'
		)
	
	if test_config is None:
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)
	
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
		
	@app.route('/hello')
	def hello():
		return 'Hello world!'
	
	from . import db
	db.init_app(app)
	
	from . import auth
	app.register_blueprint(auth.bp)
	
	from . import recipe
	app.register_blueprint(recipe.bp)
	app.add_url_rule('/', endpoint='index')
	
	return app