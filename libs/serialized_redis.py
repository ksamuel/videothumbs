# -*- coding: utf-8 -*-

"""
    Redis tools related to data serialization.
"""


from __future__ import unicode_literals, absolute_import

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.core.cache import cache

from peak.util.proxies import ObjectWrapper


class RedisClientProxy(ObjectWrapper):
    """
        Wrap the original Redis client to allow transparent serialization.
    """

    def set(self, key, value, ex=None):

        if value is not None:
            value = pickle.dumps(value)

        self.__subject__.set(key, value)

        if ex:
            self.expire(key, ex)


    def get(self, key):

        value = self.__subject__.get(key)

        if value is None:
            return value

        try:
            return pickle.loads(value)
        except:
            return value


    def hsetall(self, key, mapping, ex=None):
        """
            Apply "hset key field value" for all the field/value paires in
            `mapping`. Serizalize the values.

            Expiration can be passed as well, and will be set for the whole hash.
        """

        pipe = self.pipeline()
        for name, value in mapping.items():
            pipe.hset(key, name, pickle.dumps(value))

        if ex:
            pipe.expire(key, ex)

        pipe.execute()


    def hgetall(self, key):
        """
            Same as redis.hgetall, but deserialize values.
        """
        data = self.__subject__.hgetall(key)
        res = {}
        for name, value in data.items():

            if not isinstance(value, basestring):
                res[name] = value
                continue
            try:
                res[name] = pickle.loads(value)
            except:
                res[name] = value

        return res



client = RedisClientProxy(cache.client.client)
