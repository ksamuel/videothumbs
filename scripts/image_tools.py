#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" 

    Lib for image processing 

    get_blur: return blur coef of a picture. This is an implementation of the paper found here: http://www.cs.cmu.edu/~htong/pdf/ICME04_tong.pdf 
    rmsdiff : return the difference beetwen 2 images, 0 mean same images 

"""
import os
import math
import fnmatch

from PIL import ImageChops, ImageStat, Image, ImageFilter

class BlurError(Exception):
    pass

class BrightnessError(Exception):
    pass


def get_brightness(image_path):
    """
        Return perceived brightness.
        Take average pixels, then transform to "perceived brightness".
        http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
    """

    try:
        im = Image.open(image_path)
        stat = ImageStat.Stat(im)
        r,g,b = stat.mean
        return int(math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)))
    except Exception as e:
        print "Cannot get brightness: %s" % e
        return 0


def get_blur(image_path):
    """
        get blur coef of an image or a directory
    """
    blur_coef = 0

    try:
        if os.path.isdir(image_path):
            # it is a directory so take all jpg inside and calculate average blur coef
            for root, dirnames, filenames in os.walk(image_path):
                for filename in fnmatch.filter(filenames, '*.jpg'):
                    blur_coef = blur_coef + get_blur_coef(os.path.join(root, filename))
            return blur_coef
        else:
            return get_blur_coef(image_path)
    except Exception as e:
        raise BlurError("Cannot get blur: %s" % e)


def get_blur_coef(image):
    """
        Process image blur. Higher is output, cleaner is the picture
    """

    # init vars
    P = []
    blur_coef = []
    percent_crop = 90

    try:
        im = Image.open(image).convert('RGB')

        # crop image XX% (to remove black borders and stuff like that)
        # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
        w, h = im.size
        crop = (int(((w-w*percent_crop/100)/2)),
                int(((h-h*percent_crop/100)/2)),
                int(w*percent_crop/100),
                int(h*percent_crop/100))
        im = im.crop(crop)

        # get new cropped image size
        w, h = im.size

        # Separate image in 4 parts and calculate blur coef of each part
        P.append(im.crop((0, 0, int(w/2), int(h/2))))   # top left
        P.append(im.crop((int(w/2), 0, w, int(h/2))))   # top right
        P.append(im.crop((0, int(h/2), int(w/2), h)))   # bot left
        P.append(im.crop((int(w/2), int(h/2), w, h)))   # bot right

        # Calculate blur coef of each part
        blur_coef = [rmsdiff(img) for img in P]
        #print blur_coef

        # get average blur_coef of image
        average = math.fsum(blur_coef)/len(blur_coef)
        #print average

        # add parts coef that are higher than average image blur coef
        image_blur_coef = [x for x in blur_coef if x > average]
        image_blur_coef = math.fsum(image_blur_coef)/len(image_blur_coef)

        # Return blur coef
        return int(image_blur_coef)

    except Exception, e:
        print e
        return 0
 

def rmsdiff(image):
    """
        Calculate rms difference to find if image is blurred or not
    """

    # instanciate image class
    im = image
    
    # Get edges of image
    # to try : BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, and SHARPEN.    
    im = im.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.EDGE_ENHANCE).filter(ImageFilter.SMOOTH)

    # convert image to L (greyscale)
    im = im.convert('L')

    # remove white borders created by Image.filter
    w, h = im.size
    crop = 4
    im = im.crop( (crop, crop, w-crop, h-crop) )

    # get new cropped image size
    w, h = im.size

    # Create black image
    img_black = Image.new("L", (w, h), "black")

    # calculate difference beetwen black and edges images
    # return RMSE
    diff = ImageChops.difference(im, img_black)
    histogram = diff.histogram()
    sq = (value*(idx**2) for idx, value in enumerate(histogram))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(w * h))

    return rms





