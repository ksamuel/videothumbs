#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^4bqDQeFeQkuvrBZd/admin/', include(admin.site.urls)),
    url(r'^4bqDQeFeQkuvrBZd/translations/', include('rosetta.urls')),
    url(r'^', include('core.urls')),
)
