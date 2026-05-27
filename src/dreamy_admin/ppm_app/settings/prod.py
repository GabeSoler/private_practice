from django.conf.global_settings import SECURE_SSL_HOST

from .base import *

import sentry_sdk

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 300

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_NAME"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_KEY"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "https://" + URL_BASE + "." + HOST_URL + "/static/"
# config of bootstrap5, I added a theme called 'sandstone' from 'bootswatch'
BOOTSTRAP5 = {
    # The complete URL to the Bootstrap CSS theme file (None means no theme).
    "theme_url": STATIC_URL + "css/dreamy.css",
}

sentry_sdk.init(
    dsn=config("SENTRY_DSN"),
    traces_sample_rate=.8,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# resend activated all the time
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# REsend configuration and email back ends
RESEND_API_KEY = config("RESEND_API_KEY")
RESEND_SMTP_PORT = 587
RESEND_SMTP_USERNAME = "resend"
RESEND_SMTP_HOST = "smtp.resend.com"

EMAIL_HOST = RESEND_SMTP_HOST
EMAIL_USE_TLS = True
EMAIL_PORT = RESEND_SMTP_PORT
EMAIL_USE_SSL = False
EMAIL_HOST_USER = RESEND_SMTP_USERNAME
EMAIL_HOST_PASSWORD = RESEND_API_KEY
DEFAULT_FROM_EMAIL = "admin@crea-therapy.com"
