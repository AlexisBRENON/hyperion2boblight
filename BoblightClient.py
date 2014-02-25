import threading
import colorsys
import telnetlib
import sys

class MoodThread(threading.Thread):
    """docstring for MoodThread"""
    def __init__(self, connection, stopEvent):
        super(MoodThread, self).__init__()
        self.stopEvent = stopEvent
        self.connection = connection
        self.lightName = 'screen'

    def run(self):
        # Calculate the sleep time and hue increment
        sleepTime = 0.1
        hueIncrement = sleepTime / 60

        # Start the write data loop
        hue = 0.0
        self.stopEvent.clear()
        while not self.stopEvent.wait(sleepTime):
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            self.connection.write('set light %s rgb %f %f %f\n' % 
                (self.lightName, rgb[0], rgb[1], rgb[2]))
            hue = (hue + hueIncrement) % 1.0
        self.connection.write('set light %s rgb 0 0 0\n' % 
            (self.lightName))

class ColorThread(threading.Thread):
    """docstring for MoodThread"""
    def __init__(self, connection, rgb, stopEvent):
        super(ColorThread, self).__init__()
        self.stopEvent = stopEvent
        self.connection = connection
        self.lightName = 'screen'
        self.rgb = rgb

    def run(self):
        self.stopEvent.clear()
        self.connection.write('set light %s rgb %f %f %f\n' % 
            (self.lightName, self.rgb[0]/255.0, self.rgb[1]/255.0, self.rgb[2]/255.0))
        self.stopEvent.wait()
        self.connection.write('set light %s rgb 0 0 0\n' % 
            (self.lightName))

class BoblightClient(threading.Thread):
    """Thread which is connected to the boblight server"""
    def __init__(self, prioritizeList, serverAddress, serverPort):
        super(BoblightClient, self).__init__()
        self.prioritizeList = prioritizeList
        self.connection = telnetlib.Telnet(serverAddress, serverPort)
        self.connection.write('hello\n')

    def run(self):
        stopEvent = threading.Event()
        while True:
            self.prioritizeList.event.wait()
            self.prioritizeList.event.clear()
            stopEvent.set()
            with self.prioritizeList.lock:
                priorities = self.prioritizeList.priorities.keys()
                if len(priorities) > 0:
                    priorities.sort()
                    smallestPriorityCommand = self.prioritizeList.priorities[priorities[0]]
                else:
                    smallestPriorityCommand = None
            if smallestPriorityCommand:
                self.connection.write('set priority %d\n' % (priorities[0]))
                if smallestPriorityCommand == 'Mood':
                    MoodThread(self.connection, stopEvent).start()
                elif type(smallestPriorityCommand) is list:
                    ColorThread(self.connection, smallestPriorityCommand, stopEvent).start()
