#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu



from django.contrib.auth.models import AbstractUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin

class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    """
        Custom user with email confirmation.
    """
    pass