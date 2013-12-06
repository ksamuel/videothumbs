#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from .base import *

DEBUG = True

ALLOWED_HOST = ['*']

MIDDLEWARE_CLASSES += (
    'django_quicky.middleware.StaticServe',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    "django_quicky.context_processors.settings",
)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jabberwokee1@gmail.com'



TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

DOMAIN_NAME = '127.0.0.1:8000'

try:
    from videothumbs_project.settings.local_settings import *
except ImportError:
    pass
