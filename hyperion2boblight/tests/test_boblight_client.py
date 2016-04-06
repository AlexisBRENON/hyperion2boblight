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

    # ###########################################
    # FIXTURES

    @pytest.yield_fixture
    def boblightd_process(self):
        boblight_path = subprocess.check_output(
            'which boblightd',
            shell=True,
            universal_newlines=True).strip()
        boblight_server = subprocess.Popen(
            [boblight_path, '-c', './include/boblight/boblight.conf'],
            universal_newlines=True,
            stderr=subprocess.PIPE
        )
        while True:
            if 'setup succeeded' in boblight_server.stderr.readline():
                break

        yield boblight_server

        boblight_server.terminate()
        boblight_server.wait(10)
        time.sleep(1)

    @pytest.yield_fixture
    def boblightd_commands(self, boblightd_process):
        try:
            boblightd_commands = open('/tmp/boblight_test', 'r')
        except FileNotFoundError:
            time.sleep(2)
            boblightd_commands = open('/tmp/boblight_test', 'r')

        yield boblightd_commands

        boblightd_commands.close()

    @pytest.yield_fixture
    def boblightd(self, boblightd_process, boblightd_commands):
        yield (boblightd_process, boblightd_commands)

    @pytest.yield_fixture
    def tested_client(self, request, boblightd):
        """ Create the Boblight client which will be tested """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list.clear()
        client = BoblightClient(
            ("localhost", 19333),
            my_priority_list
        )

        yield client

    @pytest.yield_fixture
    def running_client(self, tested_client):
        client_thread = threading.Thread(target=tested_client.run)
        client_thread.start()

        yield tested_client

        tested_client.priority_list.put(0, "quit")
        client_thread.join()

    # ###########################################
    # TESTS

    def test_boblight_client_create(self, boblightd, tested_client):
        """ Check that client creation has no problem """
        expected = '{}:{} connected'.format(*tested_client.socket.getsockname())
        assert expected in boblightd[0].stderr.readline()

    def test_boblight_client_say_hello(self, boblightd, tested_client):
        """ Check that hello message is received by Boblight server """
        expected = '{}:{} said hello'.format(*tested_client.socket.getsockname())
        boblightd[0].stderr.readline()
        tested_client.say_hello()
        assert expected in boblightd[0].stderr.readline()

    def test_boblight_client_get_lights(self, boblightd, tested_client):
        """ Check that client handles light configuration """
        tested_client.say_hello()
        tested_client.get_lights()
        assert sorted([light.name for light in tested_client.lights.values()]) == sorted(['right', 'left'])
        assert tested_client.lights['left'].left == 0
        assert tested_client.lights['left'].right == 0.5
        assert tested_client.lights['right'].left == 0.5
        assert tested_client.lights['right'].right == 1

    def test_boblight_client_set_color(self, boblightd, running_client):
        """ Check that adding a color message to the priority list the client send the right
        commands to the server. """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "{0[0]}:{0[1]} priority set to {1}".format(
            running_client.socket.getsockname(),
            128
        )
        expected_command = ' '.join(['{:01.6f}'.format(128/255)]*6)
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_set_color_with_higher_priority(self, boblightd, running_client):
        """ Check that the client doesn't react when a non prioritary item is added """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        # Adding a higher priority should not react
        expected_output = "{0[0]}:{0[1]} priority set to {1}".format(
            running_client.socket.getsockname(),
            128
        )
        expected_command = ' '.join(['{:01.6f}'.format(128/255)]*6)
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        MY_PRIORITY_LIST.put(255, [255, 255, 255])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_set_color_with_lower_priority(self, boblightd, running_client):
        """ Check that client react when adding a new prioritary item """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "{0[0]}:{0[1]} priority set to {1}".format(
            running_client.socket.getsockname(),
            '{}'
        )
        expected_command = ' '.join(['{:01.6f}'.format(1/255)]*6)
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        assert expected_output.format(128) in boblightd[0].stderr.readline()
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output.format(1) in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_change_current_command(self, boblightd, running_client):
        """ Check that client react when changing the current item """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "priority set to {}".format(1)
        expected_command = ' '.join(['{:01.6f}'.format(1/255)]*6)
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

        expected_output = "priority set to {}".format(1)
        expected_command = ' '.join(['{:01.6f}'.format(11/255)]*6)
        MY_PRIORITY_LIST.put(1, [11, 11, 11])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_change_any_command(self, boblightd, running_client):
        """ Check that client doesn't react when changing a non current item """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "priority set to {}".format(128)
        expected_command = ' '.join(['{:01.6f}'.format(128/255)]*6)
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

        expected_output = "priority set to {}".format(1)
        expected_command = ' '.join(['{:01.6f}'.format(1/255)]*6)
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

        # No changement in command
        expected_command = ' '.join(['{:01.6f}'.format(1/255)]*6)
        MY_PRIORITY_LIST.put(128, [64, 64, 64])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_remove(self, boblightd, running_client):
        """ Check client fetch the second item when removing the first """
        # Read up to the 'said hello' message
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "priority set to {}".format(1)
        expected_command = ' '.join(['{:01.6f}'.format(1/255)]*6)
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

        expected_output = "priority set to {}".format(0)
        expected_command = ' '.join(['{:01.6f}'.format(0/255)]*6)
        MY_PRIORITY_LIST.remove(1)
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()
        assert expected_command in boblightd[1].readline()

    def test_boblight_client_rainbow_effect(self, boblightd, running_client):
        """ Check that client handle the rainbow effect """
        while True:
            if boblightd[0].stderr.readline().endswith('said hello\n'):
                break

        expected_output = "priority set to {}".format(1)
        MY_PRIORITY_LIST.put(1, 'Rainbow')
        time.sleep(0.1)
        boblightd[1].seek(0, io.SEEK_END)
        time.sleep(0.1)
        assert expected_output in boblightd[0].stderr.readline()

