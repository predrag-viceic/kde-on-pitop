#!/usr/bin/python

import os
scriptdir=os.path.dirname(os.path.realpath(__file__))
activate_this = scriptdir+'/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import pydbus
import sys
import glob
import re

def find_subtitles(filename) :
 print("get subtitles for file :"+filename)
 filename_without_extension=os.path.splitext(filename)[0]
 filename_without_extension = re.sub(r'([\[\]])', '[\\1]',filename_without_extension)
 subtitle_list=glob.glob(filename_without_extension+"*.srt")
 return subtitle_list			  

#main

if len(sys.argv)!=2 :
 print("Usage: playmovie.py filename")
 exit(0)


from pydbus import SessionBus
bus = SessionBus()
screensaver = bus.get('org.freedesktop.ScreenSaver', '/ScreenSaver')
cookie = screensaver.Inhibit("Omxplayer","playing movie")

 
filename = sys.argv[1]
subtitles = find_subtitles(filename)

subtitles_command_argument="" if len(subtitles)==0 else "--subtitles "+subtitles[0]

os.system("/usr/bin/omxplayer --vol 100 -b -o hdmi "+subtitles_command_argument+" "+filename);

# Don't really need to uninhiit as this will bedone on pocess exit.
screensaver.UnInhibit(cookie)
exit(0)




