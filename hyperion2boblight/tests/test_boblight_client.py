"""
This is a module for Boblight client unit testing
"""

import io
import re
import time
import socket
import logging
import threading
import subprocess

import pytest

from hyperion2boblight import BoblightClient, PriorityList

MY_PRIORITY_LIST = PriorityList()

logging.basicConfig(level=logging.DEBUG)

class TestBoblightClient:
    """ This class contains all tests for Boblight client """

    @pytest.yield_fixture(scope='module')
    def boblightd_process(self):
        boblight_server = subprocess.Popen(
            ['/usr/local/bin/boblightd', '-c', 'include/boblight.conf'],
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

    def test_boblight_client_create(self, boblightd):
        """ Check that client creation has no problem and client send the
        welcome message """
        boblightd_output = ""
        client = BoblightClient(
            ("localhost", 19333),
            MY_PRIORITY_LIST
        )
        boblightd_output = boblightd[0].stderr.readline()
        assert '127.0.0.1:{} connected'.format(client.socket.getsockname()[1]) in boblightd_output

    def test_boblight_client_say_hello(self, boblightd):
        """ Check that client creation has no problem and client send the
        welcome message """
        boblightd_output = ""
        client = BoblightClient(
            ("localhost", 19333),
            MY_PRIORITY_LIST
        )
        boblightd[0].stderr.readline()
        client.say_hello()
        boblightd_output = boblightd[0].stderr.readline()
        assert '127.0.0.1:{} said hello'.format(client.socket.getsockname()[1]) in boblightd_output

    def test_boblight_client_get_lights(self, boblightd):
        """ Check that client creation has no problem and client send the
        welcome message """
        client = BoblightClient(
            ("localhost", 19333),
            MY_PRIORITY_LIST
        )
        client.say_hello()
        client.get_lights()
        assert client.lights == ['right', 'left']

    def test_boblight_client_set_color(self, boblightd, client):
        """ Check that adding a color message to the priority list the client send the right
        commands to the server. """
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        expected = ' '.join(['{:01.6f}'.format(128/255)]*6)
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 128'.format(client.socket.getsockname()[1]) in boblightd_output:
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
        assert boblight_output.strip() == expected

    def test_boblight_client_set_color_with_higher_priority(self, boblightd, client):
        """ Check that the client doesn't react when a non prioritary item is added """
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        MY_PRIORITY_LIST.put(255, [255, 255, 255])
        # Adding a higher priority should not react
        expected = ' '.join(['{:01.6f}'.format(128/255)]*6)
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        while True:
            boblight_output = boblightd[1].readline()
            if boblight_output != '':
                break
        assert boblight_output.strip() == expected

    def test_boblight_client_set_color_with_lower_priority(self, boblightd, client):
        """ Check that client react when adding a new prioritary item """
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        expected = ' '.join(['{:01.6f}'.format(1/255)]*6)
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 1'.format(client.socket.getsockname()[1]) in boblightd_output:
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
        assert boblight_output.strip() == expected

    def test_boblight_client_change_current_command(self, boblightd, client):
        """ Check that client react when changing the current item """
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        MY_PRIORITY_LIST.put(1, [11, 11, 11])
        expected = ' '.join(['{:01.6f}'.format(11/255)]*6)
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 1'.format(client.socket.getsockname()[1]) in boblightd_output:
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
        assert boblight_output.strip() == expected

    def test_boblight_client_change_any_command(self, boblightd, client):
        """ Check that client doesn't react when changing a non current item """
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        MY_PRIORITY_LIST.put(128, [64, 64, 64])
        expected = ' '.join(['{:01.6f}'.format(1/255)]*6)
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        while True:
            boblight_output = boblightd[1].readline()
            if boblight_output != '':
                break
        assert boblight_output.strip() == expected

    def test_boblight_client_remove(self, boblightd, client):
        """ Check client fetch the second item when removing the first """
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 1'.format(client.socket.getsockname()[1]) in boblightd_output:
                break
        MY_PRIORITY_LIST.remove(1)
        expected = ' '.join(['{:01.6f}'.format(0/255)]*6)
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 0'.format(client.socket.getsockname()[1]) in boblightd_output:
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
        assert boblight_output.strip() == expected

    def test_boblight_client_rainbow_effect(self, boblightd, client):
        """ Check that client handle the rainbow effect """
        MY_PRIORITY_LIST.put(1, 'Rainbow')
        while True:
            boblightd_output = boblightd[0].stderr.readline()
            if '127.0.0.1:{} priority set to 1'.format(client.socket.getsockname()[1]) in boblightd_output:
                assert True
                break
            elif boblightd_output == '':
                assert False

