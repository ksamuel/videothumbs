# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import

from django.contrib.auth import get_user_model

from django_quicky import get_object_or_none

User = get_user_model()

class UsernameAuthBackend(object):
    def authenticate(self, username=None, password=None):
        return get_object_or_none(User, username=username)
    def get_user(self, user_id):
        return User.objects.get(pk=user_id)