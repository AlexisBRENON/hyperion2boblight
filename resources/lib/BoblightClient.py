import threading
import colorsys
import telnetlib
import utils
import sys

class RainbowThread(threading.Thread):
    """docstring for RainbowThread"""
    def __init__(self, connection, lights, stopEvent):
        super(RainbowThread, self).__init__()
        self.stopEvent = stopEvent
        self.connection = connection
        self.lights = lights

    def run(self):
        sleepTime = 0.1
        hueIncrement = sleepTime / 60

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

class BoblightClient(threading.Thread):
    """Thread which is connected to the boblight server"""
    def __init__(self, prioritiesList, serverAddress, serverPort):
        super(BoblightClient, self).__init__()
        self.prioritiesList = prioritiesList
        self.connection = telnetlib.Telnet(serverAddress, serverPort)
        self.connection.write('hello\n')
        self.lights = ['screen']
        utils.log_info('Boblight connection initialized.')

    def run(self):
        stopEvent = threading.Event()
        while True:
            self.prioritiesList.event.wait()
            self.prioritiesList.event.clear()
            (priority, command) = self.prioritiesList.getFirst()
            stopEvent.set()
            if command:
                utils.log_info('Executing : %s' % (command))
                self.connection.write('set priority %d\n' % (priority))
                if command == 'Rainbow':
                    RainbowThread(self.connection, self.lights, stopEvent).start()
                elif type(command) is list:
                    for light in self.lights:
                        self.connection.write('set light %s rgb %f %f %f\n' % 
                            (light,
                            command[0]/255.0,
                            command[1]/255.0,
                            command[2]/255.0))
                self.connection.read_eager()
        utils.log_error('Boblight connection closed unexpectedly.')
