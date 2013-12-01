# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


from django.conf import settings
from django.core.mail import send_mail


def send_admin_page_url(username, email):
        send_mail('[VideoThumbs] You admin page URL',
                  'http://{domain}/user/{username}/admin/'.format(
                  domain=settings.DOMAIN_NAME, username=username),
                  settings.EMAIL_HOST_USER, [email])


def send_confirmation_email(username, confirmation_key, email):

    send_mail('[VideoThumbs] Please confirm your email',

              """
Go to

http://{domain}/confirm/{username}/{key}/

to confirm your email address.

              """.format(domain=settings.DOMAIN_NAME,
                         username=username,
                         key=confirmation_key),
                         settings.EMAIL_HOST_USER, [email])