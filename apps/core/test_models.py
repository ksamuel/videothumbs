# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


import pytest

from django.contrib.auth import get_user_model

from .models import Options, Batch

from libs.testing_tools import redis


@pytest.fixture
def user():
    return get_user_model().objects.create(username="test")


@pytest.fixture
def options(user):
    return Options.objects.create(name="test", user=user)


@pytest.fixture
def batch(options, redis):
    return Batch.objects.create(options=options)

@pytest.mark.django_db
def test_options(options):
    assert Options.objects.all()[0] == options


@pytest.mark.django_db
def test_batch(batch, redis):
    assert batch.get_status() is None

    with pytest.raises(ValueError):
        batch.set_status('yolo')

    batch.set_status('downloading')

    batch.get_status() == redis.get(batch.status_key(batch.uuid)) == 'downloading'