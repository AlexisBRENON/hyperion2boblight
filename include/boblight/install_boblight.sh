#!/bin/sh

set -eux

# Install boblight from repo
svn checkout http://boblight.googlecode.com/svn/trunk/ boblight
cd boblight && \
  ./configure --prefix=/usr --without-portaudio --without-libusb --without-spi --without-x11 --without-opengl && \
  make && \
  sudo make install && \
  cd -

# Test boblight availability
which boblightd || exit 1
