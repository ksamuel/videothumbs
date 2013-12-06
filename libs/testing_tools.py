# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


import pytest

from path import path


from serialized_redis import RedisClientProxy, client as redis_client_proxy

from redis import Redis


@pytest.yield_fixture
def redis():
    bak = redis_client_proxy.__subject__
    redis_client_proxy.__subject__ = RedisClientProxy(Redis(db=15))
    try:
        redis_client_proxy.flushdb()
        yield redis_client_proxy
    finally:
        redis_client_proxy.flushdb()
        redis_client_proxy.__subject__ = bak


@pytest.yield_fixture
def images_dir(settings, tmpdir):
    settings.IMG_DIR = path(tmpdir) / 'images'
    settings.IMG_DIR.makedirs_p()
    yield settings.IMG_DIR

