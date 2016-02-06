"""
This is a module for Boblight client unit testing
"""

import time
import socket
import logging
import threading

import pytest

from hyperion2boblight import BoblightClient, PriorityList

MY_PRIORITY_LIST = PriorityList()

logging.basicConfig(level=logging.DEBUG)

class TestBoblightClient:
    """ This class contains all tests for Boblight client """

    @pytest.yield_fixture(scope='module')
    def server(self):
        """ Create a simple socket which act as a Boblight server to allow
        tests to assert on messages sent by the client """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("localhost", 19444))
        server_socket.listen(5)

        yield server_socket

        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()

    @pytest.yield_fixture
    def client(self, request):
        """ Create the Boblight client which will be tested """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list.clear()
        client = BoblightClient(
            ("localhost", 19444),
            my_priority_list
        )

        client_thread = threading.Thread(target=client.run)
        client_thread.start()

        yield client

        my_priority_list.put(0, "quit")
        client_thread.join()

    @pytest.fixture
    def connection(self, server, client):
        """ Create the server and the client and link them """
        connection, _ = server.accept()
        time.sleep(0.1) # Let time to the client to send welcomed messages
        return connection


    def test_boblight_client_create(self, connection):
        """ Check that client creation has no problem and client send the
        welcome message """
        received = connection.makefile().readline()
        assert received == "hello\n"

    def test_boblight_client_set_color(self, connection):
        """ Check that adding a color message to the priority list the client send the right
        commands to the server. """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        assert rfile.readline() == "set priority 128\n"
        assert rfile.readline() == "set light screen rgb %f %f %f\n" % (
            128/255.0, 128/255.0, 128/255.0
        )

    def test_boblight_client_set_color_with_higher_priority(self, connection):
        """ Check that the client doesn't react when a non prioritary item is added """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command

        MY_PRIORITY_LIST.put(255, [255, 255, 255])
        connection.settimeout(2)
        # Adding a higher priority should not react, so no message is sent
        with pytest.raises(socket.timeout):
            connection.recv(1024)

    def test_boblight_client_set_color_with_lower_priority(self, connection):
        """ Check that client react when adding a new prioritary item """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        assert rfile.readline() == "set priority 1\n"
        assert rfile.readline() == "set light screen rgb %f %f %f\n" % (
            1/255.0, 1/255.0, 1/255.0
        )

    def test_boblight_client_change_current_command(self, connection):
        """ Check that client react when changing the current item """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command

        MY_PRIORITY_LIST.put(1, [11, 11, 11])
        assert rfile.readline() == "set priority 1\n"
        assert rfile.readline() == "set light screen rgb %f %f %f\n" % (
            11/255.0, 11/255.0, 11/255.0
        )

    def test_boblight_client_change_any_command(self, connection):
        """ Check that client doesn't react when changing a non current item """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(128, [128, 128, 128])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command
        MY_PRIORITY_LIST.put(128, [64, 64, 64])
        connection.settimeout(1)
        # Changing any non first command do nothing
        with pytest.raises(socket.timeout):
            connection.recv(1024)

    def test_boblight_client_remove(self, connection):
        """ Check client fetch the second item when removing the first """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(1, [1, 1, 1])
        rfile.readline() # Receive priority
        rfile.readline() # Receive command
        MY_PRIORITY_LIST.remove(1)
        assert rfile.readline() == "set priority 0\n"
        assert rfile.readline() == "set light screen rgb %f %f %f\n" % (
            0/255.0, 0/255.0, 0/255.0
        )

    def test_boblight_client_rainbow_effect(self, connection):
        """ Check that client handle the rainbow effect """
        rfile = connection.makefile()
        rfile.readline() # Receive the hello message
        MY_PRIORITY_LIST.put(1, 'Rainbow')
        assert rfile.readline() == 'set priority 1\n'
        MY_PRIORITY_LIST.clear()
        time.sleep(0.1)

