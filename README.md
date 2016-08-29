# KDE on Pi-top

This repository contains some hints on how to use pi-top with KDE as a playground desktop for kids and Dads.

The starting point of the installation is the image from the [Minibian](https://minibianpi.wordpress.com/) project and the result is the full blown desktop environment.
I intend to document as much of the install process, so if interested, come back often ! :)

[Here](/ansible) you'll find the [Ansible](https://www.ansible.com/) playbook with basic configuration. The KDE-specific playbooks are coming ASAP.

You will have to configure the vars in pitop.yml and put the host ip  in hosts.pitop. You alse need your ssh public key in config/ssh_keys/id_dsa.pub (or similar) 

The Pi should be connected with an ethernet cable to your router.  On boot, the ip adress is displayed on the screen.

When configured, you can launch :

`ansible-playbook -k -i hosts.pitop -u root  pitop.yml --check`

When sure that you are orchestrating the correct server, remove *--check* option.


## Install KDE


## Play a movie with omxplayer

First install omxplayer:
`sudo apt-get install omxplayer`

Omxplayer plays a video over the OpenMAX hardware acceleration circuitry and outputs the result to the display framebuffer. 

The movie is rendered fullscreen and the volume is set to 0.6dB.



`/usr/bin/omxplayer --vol 600 -b -o hdmi movie.mkv`




### Use D-BUS to cancel the screensaver during movie play

We will use python to signal to the screensaver to Inhibit / UnInhibit

#### Create a python virtual environment

We need this in order to install pydbus which is not available as a Jessie package

```
 sudo aptitude install python-pip python-virtualenv python-gobject
 mkdir kde-on-pitop
 cd kde-on-pitop
 virtualenv --system-site-packages venv
 source venv/bin/activate
```

Install the pydbus library and the dependancies in the virtual environment

`pip install pydbus`


####Python script

The script inhibits the kde scrensaver and launches the omxplayer with correct settings. It also
searches for subtitles.

```python
#!/usr/bin/python

import os

#Activate the virtual environment

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

os.system("/usr/bin/omxplayer --vol 600 -b -o hdmi "+subtitles_command_argument+" "+filename);

# Don't really need to uninhibit as this will be done on process exit.
screensaver.UnInhibit(cookie)
exit(0)

```

Copy the script and the venv to /opt 

```
sudo mkdir /opt/kdeonpitop
sudo cp -R . /opt/kdeonpitop
sudo ln -s /opt/kdeonpitop/playmovie.py /usr/bin/playmovie
sudo chmod ugo+x /opt/kdeonpitop/playmovie.py
```

Play the movie !

`playmovie movie.mkv`





 
