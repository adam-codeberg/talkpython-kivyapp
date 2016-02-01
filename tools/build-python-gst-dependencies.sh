#!/usr/bin
PYENV="$1"
VER="$2"

# BUILD DEPS FOR PYTHON-GST
sudo apt-get -y install python-gst0.10
cd $PYENV/versions/$ENV/lib/python2.7/site-packages
ln -s /usr/lib/python2.7/dist-packages/glib
ln -s /usr/lib/python2.7/dist-packages/gobject
ln -s /usr/lib/python2.7/dist-packages/gst-0.10
ln -s /usr/lib/python2.7/dist-packages/gstoption.so
ln -s /usr/lib/python2.7/dist-packages/gtk-2.0
ln -s /usr/lib/python2.7/dist-packages/pygst.pth
ln -s /usr/lib/python2.7/dist-packages/pygst.py
ln -s /usr/lib/python2.7/dist-packages/pygtk.pth
ln -s /usr/lib/python2.7/dist-packages/pygtk.py


# BUILD DEPS FOR PYTHON-PYGAME
sudo apt-get -y install pygame
ln -s /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h
~/.pyenv/versions/kivy/bin/pip install http://www.pygame.org/ftp/pygame-1.9.1release.tar.gz
ln -s /usr/lib/python2.7/dist-packages/pygame

