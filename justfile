# default with just
play:
    uv run src/manage.py runserver

#start testing
test *arg:
    uv run src/manage.py test {{arg}}

#start testing
testx:
    uv run src/manage.py test --parallel

# run migrate
migrate: makemigrations
    uv run src/manage.py migrate

#rung migrate and makemigrations together
makemigrations:
    uv run src/manage.py makemigrations

#run collect static
static:
    uv run src/manage.py collectstatic

#run collect static
check:
    uv run src/manage.py check

#Allows commands passed to just manage (manage.py)
manage *arg:
    uv run src/manage.py {{arg}}

context:
    uv run src/manage.py add_context 5

shell:
    uv run src/manage.py shell -i ipython




# alias for full migrations to 'just db'
db:
    uv run src/manage.py dbshell

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

dkr:dkr-compose

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

link:
    adb reverse tcp:3000 tcp:3000
    adb usb
