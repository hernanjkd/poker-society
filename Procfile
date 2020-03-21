release: pipenv run init; pipenv run migrate; pipenv run upgrade
web: gunicorn wsgi --chdir ./src/