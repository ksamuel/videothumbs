#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


"""
    Wrapper on top of image magic. Much faster than PIL and images
    are of better quality.

    Plus, PythonMagick and other binding are a hell to install and setup.

    This module depends on envoy and minibelt.

"""


from __future__ import unicode_literals, absolute_import

import sys

import envoy

from minibelt import normalize


class ImageMagicError(Exception):
    def __init__(self, result, encoding):
        msg = normalize(result.std_err.decode(encoding))
        super(ImageMagicError, self).__init__(msg)



def size(img, encoding=sys.stdout.encoding):
    """
        Return the size of an image as a tuple (width, height).
    """
    r = envoy.run('identify -format "%[fx:w],%[fx:h]" "{}"'.format(img))

    if r.status_code != 0:
        raise ImageMagicError(r, encoding)

    w, h = r.std_out.strip().split(',')
    return int(w), int(h)


def thumb(img, width, heigth, output, crop=False, encoding=sys.stdout.encoding):

    """
        Make a thumbnail out of a file.

        If crop is set, it will try to make the image fit in the dimension
        by cropping, otherwise it will just scale it down.it

        `crop` can be set to :

        NorthWest, North, NorthEast, West, Center,
        East, SouthWest, South, SouthEast

        Which will determine was zone should be preserved. If you just pass
        "True", "Center" will be choosen.

        `fill_area` let you choose to scale down the image and fill the missing
        part with a white
    """

    if crop:
        if crop is True:
            crop = 'center'
        crop = "-gravity {} -extent {}x{}".format(crop, width, heigth)
    else:
        crop = ''

    cmd = ("convert {img} -thumbnail {width}x{heigth}^ {crop} -quality 80 {output}").format(
          img=img, width=width, heigth=heigth, crop=crop, output=output,
    )

    r =  envoy.run(cmd)

    if r.status_code != 0:
        raise ImageMagicError(r, encoding)

    return r
