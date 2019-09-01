web: gunicorn "recipemod:create_app()" --log-file -
release: export FLASK_APP=recipemod
release: export FLASK_ENV=development
release: flask init-db
