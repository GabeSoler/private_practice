FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim


# Port used by this container to serve HTTP.
EXPOSE 3000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE" command.
# 3. Disable development dependencies
# 4. Enable uv byte-code compilation
ENV PYTHONUNBUFFERED=1 \
    PORT=3000 \
    UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_MANAGED_PYTHON=1

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Add user that will be used in the container.
RUN useradd -m gsoler

# Fix ownership so the non-root user can use the venv
RUN chown -R gsoler:gsoler /app


# Install system packages required by Django and its dependencies.
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

# Copy the dependency files first to leverage Docker caching.
COPY --chown=gsoler:gsoler pyproject.toml uv.lock ./

# Switch to the non-root user BEFORE uv sync
USER gsoler

# Install dependencies using uv.
# We use --frozen to ensure the lockfile is used exactly.
RUN uv sync --frozen --no-install-project


# Copy the rest of the source code.
COPY --chown=gsoler:gsoler . .


# Runtime command that executes when "docker run" is called.
#collect static is needed at the end, so gets the env variables made dynamically
# It migrates the database and then starts Gunicorn.
CMD ["sh", "-c", "uv run src/manage.py collectstatic --nonput --clear \
      && uv run scr/manage.py migrate --noinput \
      && uv run gunicorn src.ppm_app.wsgi:application \
      --bind 0.0.0.0:$PORT" \
      --workers=6 \
      --access-log=- \
      --error-log=-]
