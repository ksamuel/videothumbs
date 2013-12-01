# -*- coding: utf-8 -*-



from __future__ import unicode_literals, absolute_import

import pytest

from serialized_redis import RedisClientProxy, client as redis_client_proxy

from redis import Redis


@pytest.yield_fixture
def redis():
    bak = redis_client_proxy.__subject__
    redis_client_proxy.__subject__ = RedisClientProxy(Redis(db=15))
    redis_client_proxy.flushdb()
    yield redis_client_proxy
    redis_client_proxy.flushdb()
    redis_client_proxy.__subject__ = bak


def test_get_set(redis):

    redis.set('a', 1)

    assert redis.get('a') == 1

    redis.set('b', ['a', 1, {True: None}])

    assert redis.get('b') == ['a', 1, {True: None}]


def test_hgetall_hsetall(redis):
    redis.hsetall('c', {'a':1, 'b':True})
    assert redis.hgetall('c') == {'a':1, 'b':True}

