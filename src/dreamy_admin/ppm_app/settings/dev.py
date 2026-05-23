from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_NAME', default='ppm_app'),
        'USER': config('POSTGRES_USER', default='gsole'),
        'PASSWORD': config('POSTGRES_KEY', default=''),
        'HOST': config('POSTGRES_HOST', default='localhost'),
        'PORT': config('POSTGRES_PORT', default='5432'),
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
