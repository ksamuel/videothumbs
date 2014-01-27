# -*- coding: utf-8 -*-

import os
import math
import tempfile
import subprocess
import pexpect
import shutil

from PIL import ImageStat, Image, ImageOps

from distutils import spawn

from image_tools import get_blur

# working paths
WORK_DIR = tempfile.gettempdir()
FRAMES_DIR = os.path.join(WORK_DIR, 'frames')
MASTERS_DIR = os.path.join(WORK_DIR, 'masters')
THUMBNAILS_DIR = os.path.join(WORK_DIR, 'thumbnails')

# path to tools
JPEGOPTIM_PATH = spawn.find_executable("jpegoptim")
MONTAGE_PATH = spawn.find_executable("montage")
FFPROBE_PATH = spawn.find_executable("ffprobe")
CONVERT_PATH = spawn.find_executable("convert")
FFMPEG_PATH = spawn.find_executable("ffmpeg")
    


class VideoImageError(Exception):
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


def get_duration(video):
    """
        Get the duration of a video in seconds.
    """
    try:
        cmd = [FFPROBE_PATH, '-show_format', '-loglevel', 'quiet', '-i', video]
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False).communicate()[0] 

        duration = int(float([duration.split('=')[1] for duration in out.split() if duration.split('=')[0] == 'duration' ][0]))
    except Exception as e: 
        raise VideoImageError("Unable to get seconds number for video %s : %s" % ( video, e) )
 
    if not duration:
        raise VideoImageError("Unable to get seconds number for video %s" % video)

    return duration


def time_range(video, number):
    """
        Return an xrange object generating seconds.
        
        This allows to get a series of frame that can be used for
        screenshots where each frame match the time in second.
        
        video: the path of the video file
        number: the number of frames you want
        
        The range always returns at least two frames, even
        if you ask for one.
    """


    # start: the % of the movie to skip before starting to get frames
    # stop: the % of the movie to skip after getting the frame
    # use this to allow script to make screenshot of the last time interval
    # and to remove the begging of video like trailer start, movie beginning, etc
    start = 5
    stop = 5

    if number < 1:
        raise ValueError('Number should be > 0')
        
    if not 0 <= start <= 100 or not 0 <= stop <= 100 :
        raise ValueError('Start and stop must be 0-100 boundaries')
    
    seconds = get_duration(video)

    start = int(seconds * start / 100)
    if start == 0:
        start = 1
    stop = int(seconds - (seconds * stop / 100))
    
    if number == 1:
        return [(stop - start) / 2]
    
    if number == 2:
        return (start, stop)
 
    if number == 3:
        return (start, (stop - start) / 2, stop)    
    
    step = int(round((stop - start) / (number - 1)))
    res = range(start, stop, step or 1)
    
    if len(res) < number:
        res.append(stop)
    
    return res[:number]


def extract_frames(video_path, dest_dir, rate=8):
    """
        Extract all frame from given video following
        /dir/frameX.jpg 
    """

    # extract frames at 8 Hz (-r 1)
    # the most frames you have, the better chances you have to find a clear one
    destination_frame = os.path.join(dest_dir, 'frame%d.jpg')
    command = [FFMPEG_PATH,
               '-y',
               '-i', video_path,
               '-f', 'image2',
               '-vf', 'fps=fps=' + str(rate),
               '-q:v', '1', # maximum quality
               destination_frame
               ]
    print 'Extract frames : ' + ' '.join(command)

    # wait for process to finish extracting frames from video
    thread = pexpect.spawn(' '.join(command))
    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        "frame=.*"
    ])
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0: # EOF
            print "The sub process exited"
            break
        elif i == 1:
            stats_line = thread.match.group(0)
            print stats_line
            thread.close


def get_best_screenshot(video_path, master_dir, screenshots_time_range, rate=8,  frames_dir=False):
    """
        Extract a frame from a video and save it to a file in jpeg.

        video_path: video source path
        screenshots_time_range: intervals in seconds where to pick up screenshots
        frames_dir: dir where are saved video frames (must call extract_frames first )

    """

    #import ipdb; ipdb.set_trace()

    print "Time intervals: %s" % screenshots_time_range

    for i, second_start in enumerate(screenshots_time_range):

        piclist = []

        # Step is to set the last screenshot to cast a little before the next screenshot cast to avoid having similar screenshots.
        # for example screenshot 1 at 330 secs and screenshot 2 at 335 secs, screenshots would be very similars.
        # time at wich we stop analyse screenshots (begining of next thumbnail)
        step = screenshots_time_range[1] - screenshots_time_range[0]
        second_end = screenshots_time_range[i] + int((step * 0.7))

        # convert seconds to frames number
        frames_start = second_start * rate
        frames_end = second_end * rate

        master = os.path.join(master_dir, '%s.jpg' % (i + 1))

        print "Get Thumbnail N° %s" % (i + 1)
        
        # Scann all frames in times intervals
        for frame in xrange(frames_start, frames_end):

            # build path of screenshot to analyse
            currimg = os.path.join(frames_dir, 'frame%s.jpg' % frame)

            # if last image reach, stop analyze
            if not os.path.exists(currimg):
                break

            try:

                blurcoef = get_blur(currimg)            
                piclist.append((blurcoef,currimg))

                print 'Check img : frame %s - blur factor: %s' % (currimg, blurcoef)
                
            except Exception as e:
                print 'Get Best Screenshot error: %s' % e
                break

        # sort blur pics to get the one the the highest coef = most clear
        piclist = sorted(piclist, key=lambda coef: coef[0])[-1][1]
        shutil.copy(piclist, master)

        print 'Select best thumbnail: %s' % piclist


def normalize(img_path, img_dest):
    """
        Normalize image colors, a must have
    """

    # copy source to tmp
    shutil.copy(img_path, img_dest+'tmp')

    im = Image.open(img_dest+'tmp')

    # apply auto contrast and equalization (normalize image)
    im = ImageOps.autocontrast(im, cutoff=0)

    #im = ImageOps.equalize(im)
    im.save(img_dest, 'JPEG', quality=100)

    # remove temp file
    os.remove(img_dest+'tmp') 


def make_thumbnail(from_, to_, params):
    """
        Very basic wrapper around the 'convert' command from Image
        Magic. Call the commands almost directly.
        
        Params should be a convert command line with placeholders
        for the input and ouput files. E.G:

        -define jpeg:size=480x360 %(input)s -thumbnail 240x180^
        -gravity center -extent 240x180 -enhance -filter Lanczos 
        -level 5%%,100%%,1.4  -unsharp 0x2 %(ouput)s"          
        
    """  

    # Normalize image
    try: 
        normalize(from_, from_)
    except Exception as e:
        raise VideoImageError("Cannot autogama Image : %s" % e) 

    # MAke thumbnail
    try: 
        params = CONVERT_PATH + ' ' + params
        print params
        params = params.split(" ") 
        subprocess.Popen( params, shell=False, close_fds=True).communicate()
       
        print "Make thumbnail : " + str(params)

        if not os.path.exists(to_):
            raise VideoImageError("Cannot make thumbnail : %s" % to_)

        # Optimize size if jpegoptim installed
        # Jpegoptim reduce image by removing Exif, etc
        if JPEGOPTIM_PATH:
            os.system("%s --max=85 --strip-all %s" % (JPEGOPTIM_PATH, to_) )
 
    except Exception as e: 
        raise VideoImageError("Cannot make thumbnail : %s" % e)


def screenshots(settings):
    """
        Make crystal clear thumbnails from dirty video 
    """

    # Rate extraction for frames 8 frmaes per seconds here
    # higher rate mean more image > more chance to get a clean one but take more time and space
    RATE_EXTRACT = 8

    # Thumbnails settings
    IMAGE_FILTER = "-filter Lanczos -brightness-contrast 3x2 -quality 85 -adaptive-sharpen 0x0.7 -unsharp 1x1.1"
    REMOVE_BLACK_BORDERS = "-fuzz 30% -trim +repage"

    nb_screenshot = settings['screenshots']
    video_path = settings['video_path']
    
    screen_success = True

    # clean and create working dirs
    # TODO !!! to dangerous, use another method
    os.system('mkdir -p "%s"' % FRAMES_DIR)
    os.system('mkdir -p "%s"' % MASTERS_DIR)
    os.system('mkdir -p "%s"' % THUMBNAILS_DIR)
    os.system('rm -f %s/*' % FRAMES_DIR)
    os.system('rm -f %s/*' % MASTERS_DIR)
    os.system('rm -f %s/*' % THUMBNAILS_DIR)

    # get video screenshots time range
    try:
        # get video duration
        screenshots_time_range = time_range(video_path, nb_screenshot)
    except (TypeError, VideoImageError) as e:
        # Cannot get video length
        print "Cannot get frame intervals"
        return

    # Extract Frames from video
    try:
        extract_frames(video_path, FRAMES_DIR, rate=RATE_EXTRACT)
    except Exception as e:
        print "Problem extracting all frames %s" % e
        return

    # make masters = select raw thumbnails based on blur coef
    try:
        get_best_screenshot(video_path=video_path,
                            master_dir=MASTERS_DIR,
                            screenshots_time_range=screenshots_time_range,
                            rate=RATE_EXTRACT,
                            frames_dir=FRAMES_DIR)
    except Exception, e:
        print e
        return

    # get best screenshot and make thumbnail with filters
    try:
        infos = {'brightness': {}, 'blur_coef': {}}
        for x in range(1, nb_screenshot + 1):
            
            print "Make thumbnails %s" % x

            # Master thumbnail path
            master = os.path.join(MASTERS_DIR, '%s.jpg' % x)

            # Name of thumbnails
            thumbnail_path = os.path.join(THUMBNAILS_DIR, '%s.jpg' % x)

            # Do not remove black borders
            if not settings['trim']:
                REMOVE_BLACK_BORDERS = ''

            # setup thumbnail parameters
            define_size = str(settings['width']*2) + 'x' + str(settings['height']*2)
            thumbnail_size = str(settings['width']) + 'x' + str(settings['height'])
            thumbnail_settings = "-define jpeg:size=%(define)s %(input)s %(remove_black_borders)s -shave 1x1 -thumbnail %(thumbnail_size)s^ -gravity %(gravity)s -extent %(thumbnail_size)s %(image_filter)s %(ouput)s" % {'define': define_size, 'thumbnail_size': thumbnail_size, 'gravity': settings['gravity'], 'image_filter': IMAGE_FILTER, 'remove_black_borders': REMOVE_BLACK_BORDERS, 'input':master, 'ouput': thumbnail_path}

            print "Setting used to make thumbnail: %s" % thumbnail_settings

            # Make the thumbnails
            make_thumbnail(master, thumbnail_path, thumbnail_settings)

            # Calculate blur_coef and brightness of each thumbnails 
            image_blur = get_blur(thumbnail_path)
            image_brightness = get_brightness(thumbnail_path)
            infos['blur_coef'][x] = int(image_blur)
            infos['brightness'][x] = int(image_brightness)

        return infos

    except Exception, e:
        raise e
        print 'Error making screenshots'


# use it as standalone to test each functions
if __name__ == '__main__':
    test = {'video_path': 'test.mp4',
            'gravity': 'center',
            'ratio_policy': 'crop',
            'screenshots': 15,
            'width': 360,
            'height': 240,
            'trim': True}

    print screenshots(test)



