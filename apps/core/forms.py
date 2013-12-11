# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import

from django import forms

from .models import ThumbnailSettings


class ThumbnailSettingsForm(forms.ModelForm):

    class Meta:
        model = ThumbnailSettings
        excludes = ['gravity', 'ratio_policy']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ThumbnailSettingsForm, self).__init__(*args, **kwargs)

    def save(self):
        ts = super(ThumbnailSettingsForm, self).save(commit=False)
        ts.user = self.user
        ts.save()
        return ts
