#!/usr/bin/python3
#
# Convert videos to meet Lectary's zip-package requirements.
#
import argparse
import sys, os, subprocess
from pathlib import Path

#FFMPEG="/PATH/TO/FFMPEG"
FFMPEG = "ffmpeg"
#FFPROBE= "/PATH/TO/FFPROBE"
FFPROBE= "ffprobe"
# extensions of valid video formats
VALID_EXTENSIONS = (".mp4",".mov",".mpeg",".mpg", "mp2", "mpeg2") # lower case file extensions of allowed source file formats


#
# checks command line parameters.
# returns sanitized variables.
# stops the script, if errors are found.
#
# based on: https://www.bogotobogo.com/python/python_argparse.php
#
def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Script to convert video files to the defined Lectary video format.')
    parser.add_argument('-i', '--inputdir',
                        required='True',
                        help='Path to the directory that holds the original video files'
                       )		
    parser.add_argument('-o', '--outputdir',
                        required='True',
                        help='Path to the directory where converted videos are saved to'
                       )		
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Prints a lot of (unneccessary) output.'
                       )
    results = parser.parse_args(args)

    results.inputdir = os.path.join(results.inputdir, '') # add the trailing slash if it's not already there
    results.outputdir = os.path.join(results.outputdir, '')
    
    if not os.path.isdir (str(results.inputdir)):
        print ("ERROR: input directory does not exist!")
        sys.exit()
    if not os.path.isdir (str(results.outputdir)):
        print ("ERROR: output directory does not exist!")
        sys.exit()
   
    return (
            results.inputdir,
            results.outputdir,
            results.verbose,
           )

#
# runs ffmpeg-/ffprobe commands.
# returns complete output of the command as a string.
# if the ffmpeg/ffprobe-command fails the script stops here.
#
def run_ffmpeg (command):
    
    if (verbose):
        print ("command:" + " ".join(command))

    try:
        ffmpeg = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg_output = ffmpeg.communicate()
    except subprocess.CalledProcessError as err:
        print ("ERROR:", err)
        sys.exit()
    else:
        ff_string = str(ffmpeg_output[0], 'utf-8')+str(ffmpeg_output[1], 'utf-8') # convert tupel with 2 bytes arrays to one string
        if (verbose):
            print("ffstring:" + ff_string)
        return (ff_string)

#
# returns width of a video in pixel
#
# based on: https://askubuntu.com/questions/577090/one-liner-ffmpeg-or-other-to-get-only-resolution
#
def get_video_width(sourcefile):
    command = [
               FFPROBE, 
               '-v','error',
               '-select_streams', 'v:0',
               '-show_entries', 'stream=width',
               '-of', 'csv=s=x:p=0',
               sourcefile
              ]

    return (run_ffmpeg(command))

#
# converting a video file in a 2 pass procedure.
# number of pass (pass_pass, can be "1" or "2") must be stated.
# if the video_width of a video is > 800 pixel the video gets resized, otherwise not.
#
def convert_video(sourcefile, targetfile, pass_pass):
    
    video_width = int (get_video_width(sourcefile))
    if (pass_pass == "1"): # print video_width just once, not twice.
        log ("video_width: " + str(video_width))

    if ( video_width > 800 ):
        resize1="-vf"
        resize2="scale=800:-1" # keeps the aspect ratio of the original file
    else:
        resize1="-an" # dummy. if this variable is empty (i.e. "") the subsequent ffmpeg-command will fail.
        resize2="-an" # dummy. using a benign/harmless/non-dangerous command.

    command = [
               FFMPEG, 
               '-y',
               '-hide_banner',
               '-i', sourcefile,
               '-pass', pass_pass,
               '-c:v', 'libx264',
               '-b:v','200k',
               resize1, resize2,
               '-an',
               targetfile,
              ]

    return (run_ffmpeg(command))

#
# simple handler for log-output
#
show_log_only_when_loglevel_is_bigger_than=10 
def log (text, loglevel=11):
   if (loglevel > show_log_only_when_loglevel_is_bigger_than):
      print (text)

##############################################################
#
#              M     A     I     N
#
##############################################################
if __name__ == '__main__':
    in_dir, out_dir, verbose = check_arg(sys.argv[1:]) # assign values from command line to variables

    log ('input_directory: '+in_dir)
    log ('output_directory: '+out_dir)
    log ('verbose: '+ str(verbose))
    log (">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    #sys.exit()

    for file in os.listdir (in_dir):
        if file.lower().endswith(VALID_EXTENSIONS) and not file.startswith('.'):
            log ("file : " + file, 10)
            sourcefile = str(in_dir) + file
            log ("sourcefile:" + sourcefile)
            targetfile = str(out_dir) + Path (file).stem + ".mp4" # change extension to mp4
            log ("targetfile:" + targetfile)
            convert_video(sourcefile, targetfile, "1") # pass 1 
            convert_video(sourcefile, targetfile, "2") # pass 2
            log ("----------------------------")

    log (">>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    #
    #delete ffmpeg2pass-0.log
    #delete ffmpeg2pass-0.log.mbtree
    print ("done.")

