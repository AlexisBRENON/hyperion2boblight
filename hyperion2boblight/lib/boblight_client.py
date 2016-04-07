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
        self.logger = logging.getLogger("BoblightClient")
        self.priority_list = priority_list # Priority list from which get the command

        self.lights = {} # Boblight server lights
        self.message = "" # Message to send to the server

        self.effect_threads = [] # List of launched effect
        self.effect_stop_event = threading.Event() # Threading event to stop effects

        try:
            self.socket = socket.create_connection(server_address)
        except socket.error as socket_error:
            logging.error(
                "Unable to create the connection to boblight server '%s:%d'",
                server_address[0],
                server_address[1])
            raise socket_error
        self.logger.info('Boblight connection accepted.')


    def run(self):
        """
        This function will send command to the Boblight server indefinitely. It can be
        used as a target for a threading.Thread object
        """
        self.say_hello()
        self.get_lights()

        try:
            command = self.priority_list.get_first()
            self.handle_command(command)
        except Empty:
            pass

        # wait for new command
        while True:
            try:
                command = self.priority_list.wait_new_item()
                if command[1] == 'quit':
                    break
            except Empty:
                command = None
            self.handle_command(command)

        self.logger.info('Shutting Down')
        self.effect_stop_event.set()
        for thread in self.effect_threads:
            thread.join()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def handle_command(self, command):
        """ Main worker """
        # No command given, turn off lights
        if command is None:
            self.logger.debug("Turning off the lights")
            self.set_priority(0)
            self.set_all_lights((0, 0, 0))
        else:
            self.logger.debug(
                'Executing %s:%s',
                command[0],
                command[1]
            )
            # Stop any running effect
            self.effect_stop_event.set()
            # Handle classic 'color' command
            if isinstance(command[1], list):
                self.set_priority(command[0])
                self.set_all_lights(
                    tuple([float(color)/255 for color in command[1]])
                )
            # Handle rainbow effect
            elif isinstance(command[1], str) and command[1] == 'Rainbow':
                self.set_priority(command[0])
                self.effect_threads.append(self.EffectThread(self, rainbow.RainbowEffect()))
                self.effect_threads[-1].start()
            else:
                self.logger.warning(
                    "Command not recognized : %s",
                    command[0]
                )
        # Actually send commands to the Boblight server
        self.send()

    def say_hello(self):
        """ Initiate communication with a hand shaking """
        self.message = 'hello\n'
        self.send()

        data = self.socket.recv(4096)
        if data != bytes('hello\n', "utf8"):
            self.logger.critical(
                ":say_hello(): Incorrect response from boblight server: '%s'",
                str(data, 'utf-8'))

    def get_lights(self):
        """ Get lights connected to the Boblight server """
        self.message = 'get lights\n'
        self.send()

        data = str(self.socket.recv(4096), "utf-8").strip()
        lines = data.split('\n')
        if lines[0].split()[0] != "lights":
            self.logger.error("Unable to enumerate lights")
        else:
            for line in lines[1:]:
                (_, name, _, vscan_0, vscan_1, hscan_0, hscan_1) = line.split(' ')
                self.lights[name] = BoblightLight(
                    name,
                    (hscan_0, hscan_1),
                    (vscan_0, vscan_1)
                )
            if int(lines[0].split()[1]) != len(self.lights):
                self.logger.warning(
                    "%s light(s) announced and %s found.",
                    lines[0].split()[1], len(self.lights)
                )
        self.logger.debug("Found %s lights: %s", len(self.lights), self.lights)
        return data

    def set_light(self, light, color):
        """ Set the message to set the light to the passed color.
        color must be an (r,g,b) tuple with values between 0 and 1. """
        self.message += 'set light {0} rgb {1[0]:.6f} {1[1]:.6f} {1[2]:.6f}\n'.format(
            light.name,
            color
        )


    def set_all_lights(self, color):
        """ Set the message to turn all lights to the asked color.
        color must be an (r,g,b) tuple with values between 0.0 and 1.0. """
        for light in self.lights.values():
            self.set_light(light, color)

    def set_priority(self, priority):
        """ Set the message to define the priority of the client """
        self.message += 'set priority {}\n'.format(priority)

    def send(self):
        """
        Send the current message to the the server and reset it.
        """
        if self.message != "":
            self.socket.sendall(bytes(self.message, "utf8"))
            self.message = ""


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
                for light in self.client.lights.values():
                    color = self.effect.get_color(light)
                    self.client.set_light(light, color)
                self.client.send()
                self.effect.increment()


