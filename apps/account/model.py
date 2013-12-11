# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


from django.contrib.auth.models import AbstractUser
from django_extensions.db.fields import UUIDField

from simple_email_confirmation import SimpleEmailConfirmationUserMixin


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    """
        Custom user with email confirmation.
    """
    uuid = UUIDField(db_index=True)
