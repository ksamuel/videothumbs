#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from .base import *

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jabberwokee1@gmail.com'

ALLOWED_HOSTS = []

try:
    from videothumbs_project.settings.local_settings import *
except ImportError:
    pass
