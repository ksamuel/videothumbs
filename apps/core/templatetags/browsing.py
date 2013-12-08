#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.template import Library

register = Library()


@register.inclusion_tag('admin_menu.html')
def admin_menu(request, username, tab):
    """
     Build the menu for the admin
    """
    return locals()

@register.inclusion_tag('admin_header.html')
def admin_header(request):
    """
     Build the footer for the admin header
    """
    return locals()

@register.inclusion_tag('admin_footer.html')
def admin_footer(request):
    """
     Build the footer for the admin
    """
    return locals()