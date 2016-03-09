""" BoblightClient is a module used to send commands to a BoblightServer
It fetch the commands from a priority list, send the most prioritary one
and keep the connection active.
It can launch some effects located in hyperemote2boblight.lib.effects
"""
import sys
import socket
import logging
import threading
from .effects import rainbow

from hyperion2boblight import Empty

class BoblightClient:
    """
    Client which connect to a Boblight server and send it commands from a PriorityList
    """
    def __init__(self, server_address, priority_list):
        self.server_address = server_address
        self.priority_list = priority_list
        self.effect_stop_event = threading.Event()
        self.command = None
        try:
            self.socket = socket.create_connection(self.server_address)
        except socket.error as socket_error:
            logging.error(
                "Unable to create the connection to boblight server '%s:%d'",
                self.server_address[0],
                self.server_address[1])
            raise socket_error

        self.socket.sendall(bytes('hello\n', "utf8"))
        data = self.socket.recv(4096)
        if data != bytes('hello\n', "utf8"):
            logging.critical('Incorrect response from boblight')

        self.lights = list()
        self.get_lights()
        logging.info('Boblight connection initialized.')

    def get_lights(self):
        self.socket.sendall(bytes('get lights\n', "utf8"))
        data = self.socket.recv(4096)
        data = data.decode("utf-8")
        lines = data.split('\n')
        l = lines[0].split()
        if l[0] != "lights":
            log.warn("Unable to enumerate lights")
            return
        n = int(l[1])
        for i in range(n):
            self.lights.append(lines[i+1].split(' ')[1])
        logging.debug("Found "+str(n)+" lights")

    def set_lights(self, red, green=None, blue=None):
        """ Return the string to turn all light to the asked colors """
        if isinstance(red, (list, tuple)):
            blue = red[2]
            green = red[1]
            red = red[0]

        message = ""
        for light in self.lights:
            message = message + 'set light %s rgb %f %f %f\n' % (
                light,
                red/255.0,
                green/255.0,
                blue/255.0)
        return message

    def set_priority(self, priority):
        """ Return the string to send to set the priority """
        return 'set priority %d\n' % (priority)

    def run(self):
        """
        This function will send command to the Boblight server indefinitely. It can be
        used as a target for a threading.Thread object
        """
        shutdown = False

        try:
            self.command = self.priority_list.get_first()
            self.handle_command()
        except Empty:
            pass
        while True:
            # wait for new command
            try:
                self.command = self.priority_list.wait_new_item()
                if self.command[1] == 'quit':
                    self.effect_stop_event.set()
                    break
            except Empty:
                self.command = None
            self.handle_command()

        logging.info('Shutting Down')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def handle_command(self):
        message = ""
        # No command given, turn off lights
        if self.command is None:
            message += self.set_priority(0)
            message += self.set_lights(0, 0, 0)
        else:
            logging.debug(
                'Executing %s:%s',
                self.command[0],
                self.command[1]
            )
            # Stop any running effect
            self.effect_stop_event.set()
            # Handle classic 'color' command
            if isinstance(self.command[1], list):
                message += self.set_priority(self.command[0])
                message += self.set_lights(self.command[1])
            # Handle rainbow effect
            elif isinstance(self.command[1], str) and self.command[1] == 'Rainbow':
                message += self.set_priority(self.command[0])
                rainbow.RainbowThread(self.socket, self.lights, self.effect_stop_event).start()
            else:
                logging.warning(
                    "Command not recognized : %s",
                    self.command[0]
                )
        # Actually send commands to the Boblight server
        if message != "":
            self.socket.sendall(bytes(message, "utf8"))



