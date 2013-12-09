#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import uuid

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.forms.models import modelform_factory
from django.forms import widgets

from django_quicky import routing, view

from apps.core.models import Options

from .mail import send_admin_page_url, send_confirmation_email

url, urlpatterns = routing()
urlpatterns.add_admin('hfjqgfydsqfbqsdklfh/admin/')

User = get_user_model()


@url('confirm/(?P<username>\w+)/(?P<key>\w+)/?')
@view('confirm.html')
def confirm(request, username, key):

    user = get_object_or_404(User, username=username)

    if user.is_confirmed:
        return {'type': 'error', 'message': 'This email is already confirmed.'}

    user.confirm_email(user.confirmation_key)

    if not user.is_confirmed:
        return {'type': 'error', 'message': 'Invalid confirmation key.'}

    send_admin_page_url(user.username, user.email)

    return redirect('admin', username=username)




@url('user/(?P<username>\w+)/admin/thumbnails-settings/?')
@view('admin_thumbnails_settings.html')
def admin_thumbnails_settings(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'settings'
    form = modelform_factory(Options,
                             widgets={"width": widgets.NumberInput(attrs={'class' : 'form-control tooltip-enabled',
                                                                          'data-placement' : 'top',
                                                                          'data-container' : 'body',
                                                                          'data-original-title' : Options._meta.get_field('width').help_text}),
                                      "height": widgets.NumberInput(attrs={'class' : 'form-control tooltip-enabled',
                                                                                  'data-placement' : 'top',
                                                                                  'data-container' : 'body',
                                                                                  'data-original-title' : Options._meta.get_field('height').help_text}),
                                      "screenshots": widgets.NumberInput(attrs={'class' : 'form-control tooltip-enabled',
                                                                                  'data-placement' : 'top',
                                                                                  'data-container' : 'body',
                                                                                  'data-original-title' : Options._meta.get_field('screenshots').help_text}),
                                      "name": widgets.Select(attrs={'class' : 'form-control tooltip-enabled',
                                                                                  'data-placement' : 'top',
                                                                                  'style' : 'width:50%',
                                                                                  'data-container' : 'body',
                                                                                  'data-original-title' : Options._meta.get_field('name').help_text}),
                                      "trim": widgets.CheckboxInput(attrs={'class' : 'form-control tooltip-enabled',
                                                                                  'data-placement' : 'top',
                                                                                  'data-container' : 'body',
                                                                                  'data-original-title' : Options._meta.get_field('trim').help_text})
                                     }
                             )
    return locals()


@url('user/(?P<username>\w+)/admin/upload-video/?')
@view('admin_upload_video.html')
def admin_upload_video(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'upload'
    form = modelform_factory(Options, widgets={"name": widgets.Select(attrs={'style' : 'width:50%'}) } )
    return locals()


@url('user/(?P<username>\w+)/admin/your-thumbnails/?')
@view('admin_your_thumbnails.html')
def admin_your_thumbnails(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'thumbnails'
    return locals()


@url('user/(?P<username>\w+)/admin/api/?')
@view('admin_api.html')
def admin_api(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'api'
    return locals()


@url('user/(?P<username>\w+)/admin/buy-credits/?')
@view('admin_buy_credits.html')
def admin_buy_credits(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'buy'
    return locals()


@url('404')
@view('404.html')
def error_404(request):
    return locals()


@url('user/(?P<username>\w+)/admin/?')
@view('admin_dashboard.html')
def admin(request, username):

    user = get_object_or_404(User, username=username)
    tab = 'dashboard'
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
            send_admin_page_url(user.username, user.email)
            return {'type': 'success',
                    'message': "We sent you a reminder of you admin URL by email."}

        else:
            send_confirmation_email(user.username, user.confirmation_key,
                                          user.email)
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