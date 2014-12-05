import threading
import colorsys

class RainbowThread(threading.Thread):
  """docstring for RainbowThread"""
  def __init__(self, connection, lights, stopEvent):
    super(RainbowThread, self).__init__()
    self.stopEvent = stopEvent
    self.connection = connection
    self.lights = lights

  def run(self):
    sleepTime = 0.1
    hueIncrement = sleepTime / 30

    # Start the write data loop
    hue = 0.0
    self.stopEvent.clear()
    while not self.stopEvent.wait(sleepTime):
      rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
      for light in self.lights:
        self.connection.write('set light %s rgb %f %f %f\n' % 
          (light,
          rgb[0],
          rgb[1],
          rgb[2]))
      hue = (hue + hueIncrement) % 1.0