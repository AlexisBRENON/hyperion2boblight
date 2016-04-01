""" This module implement a rainbow effect.
It will send color messages to pass through all rainbow colors :
red, yellow, green, turquoise, blue, purple.
"""

import socket
import colorsys
import threading

class RainbowThread(threading.Thread):
    """docstring for RainbowThread"""
    def __init__(self, connection, lights, stop_event):
        super(RainbowThread, self).__init__()
        self.stop_event = stop_event
        self.connection = connection
        self.connection.settimeout(1.)
        self.lights = lights

    def run(self):
        sleep_time = 0.1
        hue_increment = sleep_time / 30

        # Start the write data loop
        hue = 0.0
        self.stop_event.clear()
        # Loop execute every sleep_time second until stop_event is set
        while not self.stop_event.wait(sleep_time):
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            message = ""
            for light in self.lights:
                message = message + 'set light %s rgb %f %f %f\n' % (
                    light,
                    rgb[0],
                    rgb[1],
                    rgb[2])
            try:
                self.connection.send(message.encode())
            except socket.timeout:
                self.stop_event.set()
            hue = (hue + hue_increment) % 1.0
