""" BoblightClient is a module used to send commands to a BoblightServer
It fetch the commands from a priority list, send the most prioritary one
and keep the connection active.
It can launch some effects located in hyperemote2boblight.lib.effects
"""
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
        self.lights = []
        try:
            self.socket = socket.create_connection(self.server_address)
        except socket.error as socket_error:
            logging.error(
                "Unable to create the connection to boblight server '%s:%d'",
                self.server_address[0],
                self.server_address[1])
            raise socket_error
        logging.info('Boblight connection accepted.')

    def say_hello(self):
        """ Initiate communication with a hand shaking """
        self.socket.sendall(bytes('hello\n', "utf8"))
        data = self.socket.recv(4096)
        if data != bytes('hello\n', "utf8"):
            logging.critical("Incorrect response from boblight server: '%s'", str(data, 'utf-8'))
        return data

    def get_lights(self):
        """ Get lights connected to the Boblight server """
        self.socket.sendall(bytes('get lights\n', "utf8"))
        data = str(self.socket.recv(4096), "utf-8").strip()
        lines = data.split('\n')
        if lines[0].split()[0] != "lights":
            logging.error("Unable to enumerate lights")
        else:
            for line in lines[1:]:
                self.lights.append(line.split(' ')[1])
            assert int(lines[0].split()[1]) == len(self.lights)
        logging.debug("Found %s lights: %s", len(self.lights), self.lights)
        return data

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
        self.say_hello()
        self.get_lights()

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
        """ Main worker """
        message = ""
        # No command given, turn off lights
        if self.command is None:
            logging.debug(
                "Turning off the lights"
            )
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



