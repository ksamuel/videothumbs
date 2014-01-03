# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import

from django.conf.urls import patterns, url

from account.views import urlpatterns as account_urls

from .views import (urlpatterns, thumbnail_settings_list,
                    create_thumbnails_settings, update_thumbnails_settings)

urlpatterns += patterns('',
    url(r'user/(?P<username>\w+)/admin/thumbnails-settings/update/(?P<pk>[\w-]+)/?',
        update_thumbnails_settings, name="update_thumbnails_settings"),
    url(r'user/(?P<username>\w+)/admin/thumbnails-settings/create/?',
        create_thumbnails_settings, name="create_thumbnails_settings"),
    url(r'user/(?P<username>\w+)/admin/thumbnails-settings/?',
        thumbnail_settings_list, name="admin_thumbnails_settings"),
) + account_urls
