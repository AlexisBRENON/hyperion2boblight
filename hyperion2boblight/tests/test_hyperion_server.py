#! /usr/bin/env python3
""" Hyperion server unit tests """

import json
import socket
import threading

import pytest

from hyperion2boblight import HyperionServer, PriorityList

MY_PRIORITY_LIST = PriorityList()

class TestHyperionServer:
    """ Hyperion server test class """

    @pytest.yield_fixture
    def server(self, request):
        """ Create the decoder to test """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list.clear()
        server = HyperionServer(
            ("localhost", 19444),
            my_priority_list)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()

        yield server

        server.shutdown()
        server.server_close()

    @pytest.yield_fixture
    def sending_socket(self, server):
        """ Create a socket to send command to the decoder """
        sending_socket = socket.create_connection(server.server_address)

        yield sending_socket

        sending_socket.close()

    def test_hyperion_server_create(self, server):
        """ Check no error during decoder creation """
        assert server is not None

    def test_hyperion_server_info(self, sending_socket):
        """ Check that decoder answers to the serverinfo command """
        message = {'command':'serverinfo'}
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)
        assert reply_object['success'] is True

    def test_hyperion_server_color(self, sending_socket):
        """ Check that decoder answers to the color command and put the
        right item in the priority_list"""
        message = {
            'command':'color',
            'priority':128,
            'color':[128, 128, 128]
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)
        assert reply_object['success'] is True
        assert MY_PRIORITY_LIST.get_first() == (128, [128, 128, 128])
        assert MY_PRIORITY_LIST.size() == 1

    def test_hyperion_server_effect(self, sending_socket):
        """ Check that decoder answers to the effect command and put the
        right item in the priority_list"""
        message = {
            'command':'effect',
            'priority':128,
            'effect':{
                'name':"Rainbow.py"
            }
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)
        assert reply_object['success'] is True
        assert MY_PRIORITY_LIST.get_first() == (128, "Rainbow.py")
        assert MY_PRIORITY_LIST.size() == 1

    def test_hyperion_server_clear(self, sending_socket):
        """ Check that decoder answer to the clear command and actually
        remove the item from list """
        # Add a command to the server
        message = {
            'command':'color',
            'priority':128,
            'color':[128, 128, 128]
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        sending_socket.recv(1024)

        message = {
            'command':'clear',
            'priority':128
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)
        assert reply_object['success'] is True
        assert MY_PRIORITY_LIST.size() == 0

    def test_hyperion_server_clear_all(self, sending_socket):
        """ Check that decoder answer to the clearall command and actually
        remove items from list """
        # Add commands to the server
        for i in [1, 128, 255]:
            message = {
                'command':'color',
                'priority':i,
                'color':[i, i, i]
            }
            sending_socket.sendall(
                bytes(json.dumps(message) + '\n', 'utf-8'))
            reply = str(sending_socket.recv(1024), 'utf-8')
            reply_object = json.loads(reply)

        message = {
            'command':'effect',
            'priority':64,
            'effect':{
                'name': 'Rainbow.py'
            }
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)

        message = {
            'command':'clearall',
        }
        sending_socket.sendall(
            bytes(json.dumps(message) + '\n', 'utf-8'))
        reply = str(sending_socket.recv(1024), 'utf-8')
        reply_object = json.loads(reply)
        assert reply_object['success'] is True
        assert MY_PRIORITY_LIST.size() == 0

