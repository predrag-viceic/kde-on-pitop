# KDE on Pi-top

This repository contains some hints on how to use [Pi-top](https://www.pi-top.com/) with [KDE](https://www.kde.org/) as a playground desktop.

The starting point of the installation is the image from the [Minibian](https://minibianpi.wordpress.com/) project and the result is the full blown desktop environment.
I intend to document as much of the install process, so if interested, come back often ! :)

[Here](/ansible) you'll find the [Ansible](https://www.ansible.com/) playbook with basic configuration. The KDE-specific playbooks are coming ASAP.

You will have to configure the vars in pitop.yml and put the host ip  in hosts.pitop. You alse need your ssh public key in config/ssh_keys/id_dsa.pub (or similar) 

The Pi should be connected with an ethernet cable to your router.  On boot, the ip adress is displayed on the screen.

When configured, you can launch :

`ansible-playbook -k -i hosts.pitop -u root  pitop.yml --check`

When sure that you are orchestrating the correct server, remove *--check* option.


## Install KDE

More to come..

## Play a movie with omxplayer

First install omxplayer:
`sudo apt-get install omxplayer`

Omxplayer plays a video over the OpenMAX hardware acceleration circuitry and outputs the result to the display framebuffer. 

The movie is rendered fullscreen and the volume is set to 1dB.



`/usr/bin/omxplayer --vol 100 -b -o hdmi movie.mkv`




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

The script [python/playmovie.sh](python/playmovie.py) inhibits the kde scrensaver and launches the omxplayer with correct settings. It also searches for subtitles. 
Finally, it links the kde volume controls (kmix) to omxplayer volume via D-BUS.


Copy the script and the venv to /opt 

```
sudo mkdir /opt/kdeonpitop
sudo cp -R . /opt/kdeonpitop
sudo ln -s /opt/kdeonpitop/playmovie.py /usr/bin/playmovie
sudo chmod ugo+x /opt/kdeonpitop/playmovie.py
```

Play the movie !

`playmovie movie.mkv`





 
