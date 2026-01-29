# default with just
play:
    uv run python3 manage.py runserver

#start testing
test *arg:
    uv run python3 manage.py test {{arg}}

#start testing
testx:
    uv run python3 manage.py test --parallel

# run migrate
migrate: makemigrations
    uv run python3 manage.py migrate

#rung migrate and makemigrations together
makemigrations:
    uv run python3 manage.py makemigrations

#run collect static
static:
    uv run python3 manage.py collectstatic

#Allows commands passed to just manage (manage.py)
manage *arg:
    uv run python3 manage.py {{arg}}

context:
    uv run python3 manage.py add_context 5

shell:
    uv run python3 manage.py shell -i ipython


# alias for full migrations to 'just db'
alias db := makemigrations

redis:
    brew services start redis

alias r := redis

r_info:
    brew services info redis

r_stop:
    brew services stop redis

clean:
    uv cache clean

nix:
    nixpacks build /Users/gsole/Documents/Web-Work/private_practice --name dreamy

docker:
    colima start && \
    docker build -t ppm_app:local . && \
    docker run --rm -p 3000:3000 \
    -e DJANGO_SETTINGS_MODULE=ppm_app.dev.settings \
    -e DATABASE_URL=postgres://<user>:<password>@host.docker.internal:5432/<db> \
    ppm_app:local
