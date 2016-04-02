#!/bin/sh

set -eux

svn checkout http://boblight.googlecode.com/svn/trunk/ boblight
cd boblight && ./configure --prefix=/usr --without-portaudio && make && sudo make install
cd .. 
sudo cp ./include/boblight/boblight.conf /etc/boblight.conf

boblightd -f

sleep 1

killall boblightd


