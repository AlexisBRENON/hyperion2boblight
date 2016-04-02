"""
Rainbow light effect unit tests
"""

import io
import time
import threading
import subprocess

import pytest

from hyperion2boblight import BoblightClient, PriorityList

MY_PRIORITY_LIST = PriorityList()

class TestRainbowEffect:
    """ Raibow effect test class """

    @pytest.yield_fixture(scope='module')
    def boblightd_process(self):
        boblight_server = subprocess.Popen(
            ['/usr/bin/boblightd'],
            universal_newlines=True,
            stderr=subprocess.PIPE
        )
        while True:
            if 'setup succeeded' in boblight_server.stderr.readline():
                break

        yield boblight_server

        boblight_server.terminate()

    @pytest.yield_fixture(scope='module')
    def boblightd(self, boblightd_process):
        boblightd_commands = open('/tmp/boblight_test', 'r')

        yield (boblightd_process, boblightd_commands)

        boblightd_commands.close()

    @pytest.yield_fixture
    def client(self, request, boblightd_process):
        """ Create the Boblight client which will be tested """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list.clear()
        client = BoblightClient(
            ("localhost", 19333),
            my_priority_list
        )

        client_thread = threading.Thread(target=client.run)
        client_thread.start()

        yield client

        my_priority_list.put(0, "quit")
        client_thread.join()

    def test_rainbow_effect(self, boblightd, client):
        """ Test that the rainbow effect actually display each rainbow color """
        MY_PRIORITY_LIST.put(1, 'Rainbow')
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '{}:{} priority set to 1'.format(*client.socket.getsockname()) in boblightd_output:
                assert True
                break
            elif boblightd_output == '':
                assert False
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        while True:
            boblight_output = boblightd[1].readline()
            if boblight_output != '':
                break
        first_color_message = boblight_output
        commands = []
        # Wait a full iteration of the effect
        while True:
            color_message = boblightd[1].readline()
            if color_message != '':
                commands.append(color_message)
                if color_message != first_color_message:
                    break
        while True:
            color_message = boblightd[1].readline()
            if color_message != '':
                commands.append(color_message)
                if color_message == first_color_message:
                    break
        MY_PRIORITY_LIST.clear()
        commands = set(commands)
        # The message must contains command to light every rainbow color
        command_format = '{0:01.6f} {0:01.6f} {1:01.6f} {1:01.6f} {2:01.6f} {2:01.6f} \n'
        assert command_format.format(1., 0., 0.) in commands # Red
        assert command_format.format(1., 1., 0.) in commands # Yellow
        assert command_format.format(0., 1., 0.) in commands # Green
        assert command_format.format(0., 1., 1.) in commands # Turquoise
        assert command_format.format(0., 0., 1.) in commands # Blue
        assert command_format.format(1., 0., 1.) in commands # Purple
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '{}:{} priority set to 0'.format(*client.socket.getsockname()) in boblightd_output:
                assert True
                break
            elif boblightd_output == '':
                assert False

