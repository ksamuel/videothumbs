#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import unicode_literals, absolute_import

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from django_extensions.db.fields import UUIDField, CreationDateTimeField

from simple_email_confirmation import SimpleEmailConfirmationUserMixin

from libs.serialized_redis import client as redis


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    """
        Custom user with email confirmation.
    """
    uuid = UUIDField(db_index=True)


class Options(models.Model):

    GRAVITY = (
        ("northwest", "NorthWest"),
        ("north", "North"),
        ("northeast", "NorthEast"),
        ("west", "West"),
        ("center", "Center"),
        ("east", "East"),
        ("southwest", "SouthWest"),
        ("south", "South"),
        ("southeast", "SouthEast"),
    )

    RATIO_POLICY = (
        ("overflow", "Overflow canvas"),
        ("crop", "Crop to fit"),
    )

    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(User, editable=False)

    screenshots = models.PositiveIntegerField(default=1,
                                              help_text="How many sceenshots "
                                                        "do you want for one "
                                                        "video ?")

    width = models.PositiveIntegerField(default=240,
                                        help_text="Max width of the thumbnails."),
    height = models.PositiveIntegerField(default=180,
                                        help_text="Max height of the thumbnails."),

    ratio_policy = models.CharField(max_length=32, default='crop',
                                    choices=RATIO_POLICY,
                                    help_text=("In case the screenshot does "
                                             "not fit in the thumbnail size"
                                             " without destroying the "
                                             "width / height ratio, what to"
                                             " do ? 'crop', will remove a "
                                             "part of the picture, "
                                             "'overflow' will allow the "
                                             "picture to be bigger than the"
                                             " wanted size")
                                    )

    gravity = models.CharField(max_length=32, choices=GRAVITY, default="center",
                               help_text="If you choose to crop, this will "
                                         "tell us what part of the picture "
                                         "to preserve from being removed. "
                                         "This has no effect if your ratio "
                                         "policy is set to 'overflow'")


    name = models.CharField(max_length=128,
                            help_text="A name to save the options so you can "
                                      "reuse them later.")


    def __unicode__(self):
        return "[%s] Options : %s" % (self.user.username, self.name)



class Batch(models.Model):

    STATUS = {
        'downloading': 'Downloading video',
        'downloaded': 'Video has been downloaded',
        'screenshotting': 'Screenshotting video',
        'screenshoted': 'Screenshots are ready',
        'delivered': 'Client has been notified',
    }

    STATUS_DICT = dict(STATUS)

    uuid = UUIDField(primary_key=True)
    options = models.ForeignKey(Options)
    created = CreationDateTimeField()

    @classmethod
    def set_status_for(cls, uuid, value, expire=settings.DAY * 7):

        if value not in cls.STATUS:
            raise ValueError("Status can only be : %s" % ', '.join(cls.STATUS))

        return redis.set(cls.status_key(uuid), expire)


    def set_status(self, value, expire=settings.DAY * 7):
        self.set_status_for(self.uuid, value, expire)


    @classmethod
    def get_status_for(cls, uuid):
        return redis.get(cls.status_key(uuid))


    def get_status(self):
        return self.get_status_for(self.uuid)


    @classmethod
    def status_key(cls, uuid):
        return 'options:%s:status' % uuid


    def __unicode__(self):
        return "[%s] Batch %s for %s" % (self.created, self.uuid,
                                         self.options.user.username)