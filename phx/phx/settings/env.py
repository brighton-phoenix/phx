"""
Base env-parsing settings

Applied to all envs

See https://django-environ.readthedocs.io/
"""

import os

import environ

# app roots
django_root = environ.Path(__file__) - 3
app_root = environ.Path(django_root) - 1

# init env
env = environ.Env()

# reading .env file
environ.Env.read_env(os.path.join(app_root(), '.env'))

# Raise ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES = {
    'default': env.db(),
}

# False if not in os.environ
DEBUG = env.bool('DEBUG')
TEMPLATE_DEBUG = DEBUG

# Raise ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str('SECRET_KEY')

# Admins: A list of all the people who get code error notifications
# DJANGO_ADMINS=John:john@admin.com,Jane:jane@admin.com
ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS', default=[])]

# IP addresses to enable the debug toolbar
INTERNAL_IPS = env.list('INTERNAL_IPS', default=[])

RENDER_HOST = env.str('RENDER_EXTERNAL_HOSTNAME', None)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

SITE_URL = env.str('SITE_URL', default='http://localhost:8000/')

# App-specific settings
CONTACT_EMAIL = env.str('CONTACT_EMAIL')
DEFAULT_FROM_EMAIL = CONTACT_EMAIL
SERVER_EMAIL = CONTACT_EMAIL

# Analytics
if env.str('ANALYTICS', default=''):
    ANALYTICS = env.str('ANALYTICS')

# Twitter
if (env.str('TWITTER_CONSUMER_KEY', default='')
        and env.str('TWITTER_SECRET_KEY', default='')
        and env.str('TWITTER_OAUTH_TOKEN_KEY', default='')
        and env.str('TWITTER_OAUTH_SECRET_KEY', default='')):
    TWITTER = {
        'consumer_key': env.str('TWITTER_CONSUMER_KEY'),
        'consumer_secret': env.str('TWITTER_SECRET_KEY'),
        'oauth_token': env.str('TWITTER_OAUTH_TOKEN_KEY'),
        'oauth_secret': env.str('TWITTER_OAUTH_SECRET_KEY'),
    }

# Mailgun/email
EMAIL_BACKEND = env.str(
    'EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

if (env.str('MAILGUN_API_KEY', default='')
        and env.str('MAILGUN_SENDER_DOMAIN', default='')):
    ANYMAIL = {
        "MAILGUN_API_KEY": env.str("MAILGUN_API_KEY"),
        "MAILGUN_SENDER_DOMAIN": env.str("MAILGUN_SENDER_DOMAIN"),
        "MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
    }
