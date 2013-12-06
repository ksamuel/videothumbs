# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import

import operator

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import _get_queryset


def post_mortem(log, e, locals, reraise=True):
    log.exception('%s' % e)
    log.debug('Locals() : ')
    for item in locals.items():
        log.debug('%s=%s' % item)
    email = settings.EMAIL_HOST_USER
    if not settings.DEBUG:
        log.debug('Sending email')
        send_mail('Update event timeline failure', '', email,  [email])
    if reraise:
        raise e


def one_object_exists(klass, filters):
    """
        Check if at least one of the given filter match one object in DB.
    """
    query = Q()
    for filt in filters:
        query |= Q(**filt)

    return _get_queryset(klass).filter(query).exists()

