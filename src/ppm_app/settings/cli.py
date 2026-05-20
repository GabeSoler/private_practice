from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "cli.sqlite3",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
# config of bootstrap5, I added a theme called 'sandstone' from 'bootswatch'
BOOTSTRAP5 = {
    # The complete URL to the Bootstrap CSS theme file (None means no theme).
    "theme_url": STATIC_URL + "css/dreamy.css",
}
