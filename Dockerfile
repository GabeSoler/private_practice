FROM python:3.12-slim-trixie

# Add user that will be used in the container.
RUN useradd gsoler

# Port used by this container to serve HTTP.
EXPOSE 3000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=3000


# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Download the latest installer uv
ADD https://astral.sh/uv/0.1.0/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Disable development dependencies
ENV UV_NO_DEV=1

# Use /app folder as a directory where the source code is stored.
WORKDIR /app


# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown gsoler:gsoler /app

# Copy the source code of the project into the container.
COPY --chown=gsoler:gsoler . .

# Use user "wagtail" to run the build commands below and the server itself.
USER gsoler

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Runtime command that executes when "docker run" is called, it does the
# following:
#   1. Migrate the database.
#   2. Start the application server.
# WARNING:
#   Migrating database at the same time as starting the server IS NOT THE BEST
#   PRACTICE. The database should be migrated manually or using the release
#   phase facilities of your hosting platform. This is used only so the
#   Wagtail instance can be started with a simple "docker run" command.
CMD set -xe; uv run manage.py migrate --noinput; gunicorn ppm_app.wsgi:application
