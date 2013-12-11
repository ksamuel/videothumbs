#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import sys
import tempfile

import djcelery

from celery.schedules import crontab

from path import path

USERENA_USE_MESSAGES = False
USERENA_WITHOUT_USERNAMES = True
PROJECT_DIR = path(__file__).realpath().parent
SETTINGS_DIR = PROJECT_DIR.parent
ROOT_DIR = SETTINGS_DIR.parent
TEMP_DIR = path(tempfile.gettempdir())
APPS_DIR = ROOT_DIR / 'apps'
LIBS_DIR = ROOT_DIR / 'libs'
VAR_DIR = ROOT_DIR.parent / 'var'
IMG_DIR = VAR_DIR / 'images'
LOG_DIR = VAR_DIR / 'log'

sys.path.append(APPS_DIR)
sys.path.append(LIBS_DIR)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': VAR_DIR / 'videothumbs.sqlite',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = VAR_DIR / 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = VAR_DIR / 'static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_aa%snk3ks+%5*jp37#rrrpynfjepk2=!-d=@t_emk)n7_6no7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'videothumbs_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'videothumbs_project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'account',
    'core',

    'crispy_forms',
    'djcelery_email',
    'django_extensions',
    'djcelery',
    'south',
    'gunicorn',
    'rosetta',
    'simple_email_confirmation',
)

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CRISPY_TEMPLATE_PACK = 'bootstrap'

# Userena and Guardian settings
ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
USERENA_MUGSHOT_GRAVATAR = False
USERENA_MUGSHOT_DEFAULT = 'mm' # use mystery men image as default user pic

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_ENGINE = 'redis_sessions.session'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { # what to dump in each log
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': { # mandatory since django 1.5
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': { # send a mail to admins
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{ # print on the console
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'django':{ # write in a temp file
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10000000,
            'backupCount': 5,
        },
        'screenshot':{ # write in a temp file
            'class':'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_DIR / 'screenshot.log',
            'maxBytes': 10000000,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django.request': { # send an email to admins if a request fails
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.project': {
            'handlers': ['console', 'django'],
            'level': 'ERROR',
            'propagate': True,
        },
        'screenshot': {
            'handlers': ['console', 'screenshot'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}


CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
CULTURAL_DOC_EXPIRATION = DAY * 7
EVENT_EXPIRATION = DAY * 7

# DB connexion caching
CONN_MAX_AGE = 60

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_CREATE_MISSING_QUEUES = True
CELERY_TIMEZONE = TIME_ZONE
BROKER_URL = CELERY_RESULT_BACKEND = 'redis://guest@localhost:6379/'
CELERY_RESULT_PERSISTENT = True
CELERY_ENABLE_UTC = True


EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

# TODO ? Migrate to official celery API http://docs.celeryproject.org/en/master/whatsnew-3.1.html
djcelery.setup_loader()

ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'

AUTH_USER_MODEL = 'account.User'

DOMAINE_NAME = 'videothumbs'


AUTHENTICATION_BACKENDS = (
    'account.backends.UsernameAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)


