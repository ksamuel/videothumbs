#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import uuid

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404

from django_quicky import routing, view

url, urlpatterns = routing()
urlpatterns.add_admin('hfjqgfydsqfbqsdklfh/admin/')

User = get_user_model()


def send_admin_page_url(user):
        send_mail('[VideoThumbs] You admin page URL',
                  'http://{domain}/user/{username}/admin/'.format(
                  domain=settings.DOMAIN_NAME, username=user.username),
                  settings.EMAIL_HOST_USER, [user.email])


@url('confirm/(?P<username>\w+)/(?P<key>\w+)/?')
@view('confirm.html')
def confirm(request, username, key):

    user = get_object_or_404(User, username=username)

    if user.is_confirmed:
        return {'type': 'error', 'message': 'This email is already confirmed.'}

    user.confirm_email(user.confirmation_key)

    if not user.is_confirmed:
        return {'type': 'error', 'message': 'Invalid confirmation key.'}

    send_admin_page_url(user)

    return redirect('admin', username=username)



@url('user/(?P<username>\w+)/admin/?')
@view('admin.html')
def admin(request, username):

    user = get_object_or_404(User, username=username)
    return locals()


@url('')
@view('home.html')
def home(request):

    try:
        email = request.POST['email']
    except KeyError:
        return {}

    try:
        validate_email(email)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = uuid.uuid4().hex
            user = User.objects.create_user(username=username,
                                            email=email)

        if user.is_confirmed:
            send_admin_page_url(user)
            return {'type': 'success',
                    'message': "We sent you a reminder of you admin URL by email."}

        else:

            send_mail('[VideoThumbs] Please confirm your email',

                      """
Go to

http://{domain}/confirm/{username}/{key}/

to confirm your email address.

                      """.format(domain=settings.DOMAIN_NAME,
                                 username=user.username,
                                 key=user.confirmation_key),

                       settings.EMAIL_HOST_USER, [email])

        return {'type': 'success',
                'message': "Check your emails for a confirmation link."}
    except ValidationError:
        return {'type': 'error',
                'message': "You must pass a valid email address"}

    return {}


@url.http404
@view('raw')
def http404(request):
    return "<html><head><title>404 Error</title></head><body><h1>404 Error</h1></body></html>"