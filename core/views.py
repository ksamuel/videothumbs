#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django_quicky import routing, view

url, urlpatterns = routing()



@url('admin/?')
@view(render_to='admin.html')
def admin(request):
    return {}


@url('')
@view(render_to='home.html')
def home(request):
    return {}