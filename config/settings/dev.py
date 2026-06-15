"""Development settings."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]
