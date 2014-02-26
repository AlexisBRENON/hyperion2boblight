import threading
import telnetlib
import utils
import sys
import socket
import effects.rainbow

class BoblightClient(threading.Thread):
    """Thread which is connected to the boblight server"""
    def __init__(self, prioritiesList, serverAddress, serverPort):
        super(BoblightClient, self).__init__()
        self.prioritiesList = prioritiesList
        try:
            self.connection = telnetlib.Telnet(serverAddress, serverPort)
        except socket.error:
            utils.log_error('%s : Unable to create the Telnet connection to boblight server \'%s:%d\'' %
                (self.__class__.__name__, serverAddress, serverPort))
            self.connection = sys.stdout
        self.connection.write('hello\n')
        self.lights = ['screen']
        utils.log_info('%s : Boblight connection initialized.' %
            (self.__class__.__name__))

    def run(self):
        stopEvent = threading.Event()
        while True:
            (priority, command) = self.prioritiesList.waitNewItem()
            stopEvent.set()
            if command:
                utils.log_debug('%s : Executing %s:%s' %
                    (self.__class__.__name__, priority, command))
                self.connection.write('set priority %d\n' % (priority))
                if command == 'Rainbow':
                    effects.rainbow.RainbowThread(self.connection, self.lights, stopEvent).start()
                elif type(command) is list:
                    for light in self.lights:
                        self.connection.write('set light %s rgb %f %f %f\n' % 
                            (light,
                            command[0]/255.0,
                            command[1]/255.0,
                            command[2]/255.0))
            else:
                for light in self.lights:
                        self.connection.write('set light %s rgb 0 0 0\n' % 
                            (light))
            try:
                self.connection.read_eager()
            except AttributeError:
                pass
        utils.log_error('%s : Boblight connection closed unexpectedly.' %
            (self.__class__.__name__))
