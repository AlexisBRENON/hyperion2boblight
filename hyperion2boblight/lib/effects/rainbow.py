""" This module implement a rainbow effect.
It will send color messages to pass through all rainbow colors :
red, yellow, green, turquoise, blue, purple.
"""

import colorsys

from .effect import Effect

class RainbowEffect(Effect):
    """docstring for RainbowThread"""
    def __init__(self):
        super(RainbowEffect, self).__init__()
        self.hue = 0.0
        self.hue_increment = 1./360

    def get_color(self, light=None):
        return tuple([round(x, 4) for x in colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)])

    def increment(self):
        self.hue += self.hue_increment
        if self.hue > 1.0:
            self.hue -= 1.0

