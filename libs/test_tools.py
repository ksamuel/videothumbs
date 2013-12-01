# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


from .testing_tools import redis

def test_get_set(redis):

    redis.set('a', 1)

    assert redis.get('a') == 1

    redis.set('b', ['a', 1, {True: None}])

    assert redis.get('b') == ['a', 1, {True: None}]


def test_hgetall_hsetall(redis):
    redis.hsetall('c', {'a':1, 'b':True})
    assert redis.hgetall('c') == {'a':1, 'b':True}

