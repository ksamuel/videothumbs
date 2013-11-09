#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from .base import *

DEBUG = True

DOMAIN_NAME = '127.0.0.1:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR / 'db.sqlite',
    }
}


MIDDLEWARE_CLASSES += (
    'django_quicky.middleware.StaticServe',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    "django_quicky.context_processors.settings",
)

