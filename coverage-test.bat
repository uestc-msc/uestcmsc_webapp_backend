coverage run --source=./ manage.py test --noinput
coverage html
start htmlcov/index.html