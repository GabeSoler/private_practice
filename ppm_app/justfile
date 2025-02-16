# default with just
play:
    uv run python3 manage.py runserver

#start testing
test *arg:
    uv run python3 manage.py test {{arg}}

# run migrate
migrate:
    uv run python3 manage.py migrate

#rung migrate and makemigrations together
makemigrations: migrate
    uv run python3 manage.py makemigrations

#Allows commands passed to just manage (manage.py)
manage arg:
    uv run python3 manage.py {{arg}}

# alias for full migrations to 'just db'
alias db := makemigrations
