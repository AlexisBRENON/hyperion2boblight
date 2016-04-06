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

class BoblightLight:
    """
    A light as defined in the Boblight config file.

    It can be used by the Effect objects to return expected color given
    the scanning area of a light.

    To instanciate a light object, you must pass to its constructor values
    returned by the boblight server. Nevertheless, internally coordinates
    are stored in a relative manner : left-top corner is (0, 0) and
    right-bottom one is (1.0, 1.0).
    """

    def __init__(self, name, hscan, vscan):
        """
        Create a new light.

        name is the name of the light. It's not very useful except for debug
        informations.
        hscan and vscan are tuples, representing the scanning area coordinates,
        according to the boblight configuration (i.e. with values between 0
        and 100).
        """
        self.name = name
        self.left = float(hscan[0])/100
        self.right = float(hscan[1])/100.
        self.top = float(vscan[0])/100
        self.bottom = float(vscan[1])/100.

    @property
    def width(self):
        """
        The width property is the width of the scanning area of the light.
        """
        try:
            return self.width
        except AttributeError:
            self.width = self.right - self.left

    @property
    def height(self):
        """
        The height property is the height of the scanning area of the light.
        """
        try:
            return self.height
        except AttributeError:
            self.height = self.bottom - self.right

    def contains(self, coord):
        """
        Check that light reacts to the point with coordinates coord.
        """
        return (
            coord[0] > self.left and coord[0] < self.right and
            coord[1] > self.top and coord[1] < self.bottom
        )

    def __str__(self):
        return "-<O {} ({:.2f}-{:.2f}, {:.2f}|{:.2f})".format(
            self.name,
            self.left, self.right,
            self.top, self.bottom)

    def __repr__(self):
        return "BoblightLight({}, ({:d}, {:d}), ({:d}, {:d}))".format(
            self.name,
            int(self.left * 100), int(self.right * 100),
            int(self.top * 100), int(self.bottom *100))


class BoblightClient:
    """
    Client which connect to a Boblight server and send it commands from a PriorityList
    """
    def __init__(self, server_address, priority_list):
        self.server_address = server_address
        self.priority_list = priority_list
        self.effect_stop_event = threading.Event()
        self.effect_threads = []
        self.command = None
        self.lights = {}
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
        self.send_message('hello\n')
        data = self.socket.recv(4096)
        if data != bytes('hello\n', "utf8"):
            logging.critical("Incorrect response from boblight server: '%s'", str(data, 'utf-8'))
        return data

    def get_lights(self):
        """ Get lights connected to the Boblight server """
        self.send_message('get lights\n')
        data = str(self.socket.recv(4096), "utf-8").strip()
        lines = data.split('\n')
        if lines[0].split()[0] != "lights":
            logging.error("Unable to enumerate lights")
        else:
            for line in lines[1:]:
                (_, name, _, vscan_0, vscan_1, hscan_0, hscan_1) = line.split(' ')
                self.lights[name] = BoblightLight(
                    name,
                    (hscan_0, hscan_1),
                    (vscan_0, vscan_1)
                )
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
        for light in self.lights.values():
            message = message + 'set light %s rgb %f %f %f\n' % (
                light.name,
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
        self.effect_stop_event.set()
        for thread in self.effect_threads:
            thread.join()
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
                self.effect_threads.append(self.EffectThread(self, rainbow.RainbowEffect()))
                self.effect_threads[-1].start()
            else:
                logging.warning(
                    "Command not recognized : %s",
                    self.command[0]
                )
        # Actually send commands to the Boblight server
        if message != "":
            self.send_message(message)

    def send_message(self, message):
        self.socket.sendall(bytes(message, "utf8"))


    # Define a thread to handle effects

    class EffectThread(threading.Thread):
        """ An effect thread which sends data to the boblight server while the
        boblight client wait for new commands. """

        def __init__(self, client, effect, speed=1):
            super(BoblightClient.EffectThread, self).__init__()
            self.client = client
            self.effect = effect
            self.speed = speed/10.

        def run(self):
            self.client.effect_stop_event.clear()
            while not self.client.effect_stop_event.wait(self.speed):
                message = ""
                for light in self.client.lights.values():
                    color = self.effect.get_color(light)
                    message += "set light {} rgb {} {} {}\n".format(light.name, *color)
                self.client.send_message(message)
                self.effect.increment()


