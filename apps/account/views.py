#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404

from django_quicky import routing

url, urlpatterns = routing()

User = get_user_model()


def admin_login_required(func):
    """
       Equivalent of Django @login_required but redirects using the username
       to a custom login view.
    """

    @wraps(func)
    def wrapper(request, username, *args, **kwargs):

      if not request.user.is_authenticated():
        url = reverse('admin_login', kwargs={'username':username})
        path = request.get_full_path()
        return redirect(url + '?next=' + path)

      return func(request, username, *args, **kwargs)

    return wrapper


@url(r'user/(?P<username>\w+)/login/?')
def admin_login(request, username):
    """
       Login user based on the username in the URL.
    """
    user = authenticate(username=username)
    if user is not None:
        login(request, user)
        return redirect(request.GET['next'])
    raise Http404

