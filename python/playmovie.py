#!/usr/bin/python

import os,time


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
from gi.repository import GObject
bus = SessionBus()
screensaver = bus.get('org.freedesktop.ScreenSaver', '/ScreenSaver')
cookie = screensaver.Inhibit("Omxplayer","playing movie")

 
filename = sys.argv[1]
subtitles = find_subtitles(filename)
subtitles_file="" if len(subtitles)==0 else subtitles[0]

# link to system volume
mixer = bus.get('org.kde.kmix', '/Mixers')
device_name="/Mixers/"+mixer.currentMasterMixer.replace(":","_")
currentdevice=bus.get('org.kde.kmix', device_name)
mastercontrol=bus.get('org.kde.kmix', currentdevice.masterControl)


# Launch omxplayer
from subprocess import Popen, PIPE
import errno
omxhandle = Popen(['/usr/bin/omxplayer','--vol','0','-b','-o', 'hdmi','--subtitles',subtitles_file, filename])

#link to omxplayer DBUS 
import getpass
addressfile="/tmp/omxplayerdbus."+getpass.getuser()
pidfile="/tmp/omxplayerdbus."+getpass.getuser()+".pid"

if not os.path.isfile(addressfile):
    time.sleep(3) #Wait for dbus file to appear

with open (addressfile, "r") as myfile:
    address=myfile.readlines()[0].rstrip()

with open (pidfile, "r") as myfile:
    pid=myfile.readlines()[0].rstrip()


os.environ["DBUS_SESSION_BUS_PID"]=pid
os.environ["DBUS_SESSION_BUS_ADDRESS"]=address
   
# Subscribe to kmix controlChanged signal with a callback which calls omxplayer in a another bus
def volumeChanged():
    os.system("dbus-send --print-reply=literal --session --reply-timeout=500 --dest=org.mpris.MediaPlayer2.omxplayer /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Set string:'org.mpris.MediaPlayer2.Player' string:'Volume' double:"+("0.0" if mastercontrol.mute else str(mastercontrol.volume/100.0))+" > /dev/null")

currentdevice.controlChanged.connect(volumeChanged)

#set the initial volume
time.sleep(2) #wait for omxplayer to come up
volumeChanged()

# Callback to check periodically if omxplayer is still running. If not exit
from threading import Timer

def checkomxplayer():
  loop.quit() if omxhandle.poll() else Timer(1,checkomxplayer).start()   

checkomxplayer()

# Create and run main loop
loop = GObject.MainLoop()
loop.run()

# Don't really need to uninhibit as this will be done on process exit.
screensaver.UnInhibit(cookie)










