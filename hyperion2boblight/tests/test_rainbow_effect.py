"""
Rainbow light effect unit tests
"""

import socket
import threading

import pytest

from hyperion2boblight import BoblightClient, PriorityList

MY_PRIORITY_LIST = PriorityList()

class TestRainbowEffect:
    """ Raibow effect test class """

    @pytest.fixture(scope='module')
    def server(self, request):
        """ Create a socket which play the server's role to get message from client """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("localhost", 19444))
        server_socket.listen(5)
        def end():
            """ Terminating function """
            server_socket.close()
        request.addfinalizer(end)
        return server_socket

    @pytest.yield_fixture
    def client(self, request):
        """ Create the boblight client which will connect to our server socket """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list .clear()
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
    def connection(self, request, server, client):
        """ Actually create server and client and connect them """
        connection, _ = server.accept()
        # Receive the hello message
        connection.recv(1024)
        return connection

    def test_rainbow_effect(self, connection):
        """ Test that the rainbow effect actually display each rainbow color """
        MY_PRIORITY_LIST.put(1, 'Rainbow')
        # Receive the priority
        connection.recv(1024)
        first_color_message = connection.recv(1024).decode()
        message = ""
        # Wait a full iteration of the effect
        while message.find(first_color_message) < 0:
            message = message + connection.recv(1024).decode()
        MY_PRIORITY_LIST.clear()
        # The message must contains command to light every rainbow color
        assert message.find("rgb %f %f %f" % (1., 0., 0.)) != -1 # Red
        assert message.find("rgb %f %f %f" % (1., 1., 0.)) != -1 # Yellow
        assert message.find("rgb %f %f %f" % (0., 1., 0.)) != -1 # Green
        assert message.find("rgb %f %f %f" % (0., 1., 1.)) != -1 # Turquoise
        assert message.find("rgb %f %f %f" % (0., 0., 1.)) != -1 # Blue
        assert message.find("rgb %f %f %f" % (1., 0., 1.)) != -1 # Purple

