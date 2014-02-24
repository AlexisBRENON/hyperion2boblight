import threading
import colorsys
import telnetlib

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
        while not self.stopEvent.is_set():
            rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
            self.connection.write('set light %s rgb %f %f %f\n' % 
                (self.lightName, rgb[0], rgb[1], rgb[2]))
            hue = (hue + hueIncrement) % 1.0
            stopEvent.wait(sleepTime)
        self.stopEvent.clear()

class ColorThread(threading.Thread):
    """docstring for MoodThread"""
    def __init__(self, connection, rgb, stopEvent):
        super(ColorThread, self).__init__()
        self.stopEvent = stopEvent
        self.connection = connection
        self.lightName = 'screen'
        self.rgb = rgb

    def run(self):
        self.connection.write('set light %s rgb %f %f %f\n' % 
            (self.lightName, self.rgb[0], self.rgb[1], self.rgb[2]))
        self.stopEvent.wait()
        self.stopEvent.clear()

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
            print('New command added to list !')
            with self.prioritizeList.lock:
                priorities = self.prioritizeList.priorities.keys()
                priorities.sort()
                smallestPriorityCommand = self.prioritizeList.priorities[priorities[0]]
            print('Smallest priority : %d' % priorities[0])
            cmd = 'set priority %d' % priorities[0]
            print cmd
            #self.connection.write()
            print smallestPriorityCommand
            if smallestPriorityCommand == 'Mood':
                print 'Mood asked'
                thread = MoodThread(self.connection, stopEvent)
                thread.start()
            elif type(smallestPriorityCommand) is list:
                print 'Color asked'
                ColorThread(self.connection, smallestPriorityCommand, stopEvent).start()
