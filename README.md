# KDE on Pi-top

This repository contains some hints on how to use [Pi-top](https://www.pi-top.com/) with [KDE](https://www.kde.org/) as a playground desktop.

The starting point of the installation is the image from the [Minibian](https://minibianpi.wordpress.com/) project and the result is the full blown desktop environment.
I intend to document as much of the install process, so if interested, come back often ! :)

The minibian image should be burned on the sd card. The procedure differs depending if you are using a sd card reader or sd-to-usb adapter. For me, it amounts to:

`tar xzOf 2016-03-12-jessie-minibian.tar.gz | sudo dd of=/dev/mmcblk0`

For you this may be different. You should **never** launch this command if you are not sure about the parts coming after `of=`. You will find all the needed info at [www.raspberrypi.org](https://www.raspberrypi.org/documentation/installation/installing-images/).



[Here](/ansible) you'll find the [Ansible](https://www.ansible.com/) playbook with basic configuration. Ansible is part of the standard jessie so you can install it with:

`sudo aptitude install ansible`

If you have some spare RPis, take one and run ansible playbooks from there.

You will have to configure the vars the inventory file  [hosts.pitop](ansible/hosts.pitop). You also need your ssh public key in config/ssh_keys/id_dsa.pub (or similar) 

Ansible works over SSH and the clean way of handling this is to use a passwordless authentication. That way you keep your home-infrastructure clean, secure and reproducible. More info on [www.raspberrypi.org](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)

You do not need to copy your public keys to the destination system, ansible playbook will do this for you.

The Pi should be connected with an ethernet cable to your router.  On boot, the ip adress is displayed on the screen.

When everything is configured in hosts.pitop, you can launch :

`ansible-playbook -k -i hosts.pitop -u root  pitop.yml --check`

The default SSH password in Minibian image is [raspberry](https://minibianpi.wordpress.com/faq/). Ansible playbook will ask you the SSH password and use it for the orchestration. After the orchestration is finished  it will disable console root access.

When sure that you are orchestrating the correct server, remove `--check` option.

The playbook will take some time to run (~1h30) and will heat your CPU up to 86°C, depending on your ambient temperature. Don't touch the CPU  ! (now I'm sure you will touch it :) )

It the system hangs on reboot task (may happen), just Ctrl-C and restart the playbook.

When everything is installed, your pi will be rebooted one more time and greet you with the KDE login screen. After login, press Alt-Shift-F12 to disable desktop effects. This can be done permanently in K-> System settings-> Desktop effects

## Change screen brightness with pi-top brightness keys

First of all you should install a pi-top brightness control tool available in the [pi-top-install](https://github.com/rricharz/pi-top-install) repository.

To do this, follow the steps:

```
wget https://github.com/rricharz/pi-top-install/archive/master.zip
unzip master.zip
mkdir -p /opt/kde-on-pitop/
sudo cp pi-top-install-master/brightness /opt/kde-on-pitop/
sudo ln -s /opt/kde-on-pitop/brightness /usr/bin/brightness
```

Now you can execute:
```
brightness decrease
brightness increase
```
 
The last thing to do is to map pi-top brightness keys to the playmovie command.

First you should add a `/etc/X11/Xmodmap` file with the following content:

```
keycode 199 = XF86MonBrightnessUp 
keycode 198 = XF86MonBrightnessDown
```

And then execute :
```
xmodmap /etc/X11/Xmodmap
```

This will make the Pi-top brightness buttons available to KDE shortcut manager.

In order to make this modification permanent,you should add a new file to your global X11 configuration:

`sudo vim /etc/X11/Xsession.d/25x11-xmodmap`

and put the following content:

`[ -f /etc/X11/Xmodmap ] && xmodmap /etc/X11/Xmodmap`

Finally we must tell to KDE the new mapping. This is done in System Configuration -> Shortcuts and gestures -> Custom shortcuts :

- Edit -> New -> Global shortcut -> URL / Command
- Rename "New action" to Pi-top brightness up
- In Triggers tab type the brightness up key on your keyboard
- In Action tab enter `sudo /usr/bin/brightness increase'

Do the same for brightness down key.
- Edit -> New -> Global shortcut -> URL / Command
- Rename "New action" to Pi-top brightness down
- In Triggers tab type the brightness down key on your keyboard
- In Action tab enter `sudo /usr/bin/brightness decrease'

Click apply !

You can also import the provided [pi-top-brightness.khotkeys](ansible/roles/kde/files/pi-top-brightness.khotkeys) file. You will however need to re-affect the brightness keys in GUI because by  default they are handled by kded.

Now the pi-top keys should control the brightness of the screen.

If you don't want to run brightness binary with sudo privileges, do as described 
[here](http://quick2wire.com/non-root-access-to-spi-on-the-pi/)



## Shutdown the screen back-light on screen-saver event

`brightness` binary can be used with *on* and *off* command line parameters which allow to shut off/on the piTop screen backlight. We will use this to shut down the screen when the screensaver kicks in, and to bring it up when you screensaver stops.

First you should configure the screensaver, ie:
`cp ansible/roles/kde/files/kscreensaverrc ~/.kde/share/config/ `

And then link this event with the `brightness` binary:
`cp ansible/roles/kde/files/ksmserver.notifyrc ~/.kde/share/config/`

After 60 seconds of inactivity, you screen should go off. It should wakeup on keyboard or mouse event.
We do not lock the screen with a password as this is primarily intended as power-saving feature. 





## Play a movie with omxplayer

First install omxplayer:
`sudo aptitude install omxplayer`

Omxplayer plays a video over the OpenMAX hardware acceleration circuitry and outputs the result to the display framebuffer. 

The movie is rendered fullscreen and the volume is set to 1dB.



`/usr/bin/omxplayer --vol 100 -b -o hdmi movie.mkv`




### Use D-BUS to cancel the screensaver during movie play

We will use python to signal to the screensaver to Inhibit / UnInhibit

#### Create a python virtual environment

We need this in order to install pydbus which is not available as a Jessie package

```
 sudo aptitude install python-pip python-virtualenv python-gobject dbus
 mkdir kde-on-pitop
 cd kde-on-pitop
 virtualenv --system-site-packages venv
 source venv/bin/activate
```

Install the pydbus library and the dependancies in the virtual environment

`pip install pydbus`


####Python script

The script [python/playmovie.py](python/playmovie.py) inhibits the kde screensaver and launches omxplayer with correct settings. It also searches for subtitles. 
Finally, it links the kde volume controls (kmix) to omxplayer volume via D-BUS.


Copy the script and the venv to /opt 

```
cd kde-on-pitop/python
sudo mkdir /opt/kdeonpitop
sudo cp -R . /opt/kdeonpitop
sudo ln -s /opt/kdeonpitop/playmovie.py /usr/bin/playmovie
sudo chmod ugo+x /opt/kdeonpitop/playmovie.py
```

Play the movie !

`playmovie movie.mkv`

If you want to link your video files to this script so you can click directly from Dolphin, do the following:

```
sudo cp kde-on-pitop/ansible/roles/omxplayer/files/omxwrapper.desktop /usr/share/applications/
sudo chmod 644 /usr/share/applications/omwrapper.desktop 
sudo aptitude install desktop-file-utils
sudo update-desktop-database
sudo kbuildsycoca4
xdg-mime default omxwrapper.desktop video/mp4
xdg-mime default omxwrapper.desktop video/x-matroska
```

This can also be configured with the GUI, but where's the fun in that :)


















 
