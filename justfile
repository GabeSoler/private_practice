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
db:
    uv run manage.py dbshell

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

dkr:
    docker build -t ppm_app:local . && \
    docker run --rm -p 3000:3000 \
    --env-file ppm_app/.env.dk \
    -e DJANGO_SETTINGS_MODULE=ppm_app.settings.dev \
    ppm_app:local

dkr-run:
  docker run --rm -p 3000:3000 \
  --env-file ppm_app/.env.dk \
  -e DJANGO_SETTINGS_MODULE=ppm_app.settings.dev \
  ppm_app:local

dkr-build:
     docker build -t ppm_app:local

dkr-compose:
    docker compose -f docker-compose.dev.yml up --build


playwright:
    uv run -m playwright codegen http://127.0.0.1:8000
