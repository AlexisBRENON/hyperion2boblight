""" Hyperion server unit tests """
import pytest
import socket
import json
import hyperemote2boblight.lib.hyperion_decoder as hyperion_decoder
import hyperemote2boblight.lib.priority_list as priority_list

MY_PRIORITY_LIST = priority_list.PriorityList()

class TestHyperionServer:
    """ Hyperion server test class """

    @pytest.fixture
    def decoder(self, request):
        """ Create the decoder to test """
        my_priority_list = getattr(request.module, "MY_PRIORITY_LIST", None)
        my_priority_list.clear()
        decoder = hyperion_decoder.HyperionDecoder(
            my_priority_list,
            "localhost", 19444)
        def end():
            """ Terminating function for decoder """
            sending_socket = socket.create_connection(("localhost", 19444))
            message = {'command':"quit"}
            sending_socket.send(json.dumps(message).encode())
            sending_socket.shutdown(socket.SHUT_RDWR)
            sending_socket.close()
            decoder.join()
        request.addfinalizer(end)
        decoder.start()
        return decoder

    @pytest.fixture
    def sending_socket(self, request):
        """ Create a socket to send command to the decoder """
        sending_socket = socket.create_connection(("localhost", 19444))
        def end():
            """ Terminating function """
            sending_socket.shutdown(socket.SHUT_RDWR)
            sending_socket.close()
        request.addfinalizer(end)
        return sending_socket

    def test_hyperion_server_create(self, decoder):
        """ Check no error during decoder creation """
        assert decoder != None

    def test_hyperion_server_info(self, decoder, sending_socket):
        """ Check that decoder answers to the serverinfo command """
        message = {'command':'serverinfo'}
        sending_socket.send(json.dumps(message).encode())
        reply = sending_socket.recv(1024).decode()
        reply_object = json.loads(reply)
        assert reply_object['success'] == True

    def test_hyperion_server_color(self, decoder, sending_socket):
        """ Check that decoder answers to the color command and put the
        right item in the priority_list"""
        message = {
            'command':'color',
            'priority':128,
            'color':[128, 128, 128]
        }
        sending_socket.send(json.dumps(message).encode())
        reply = sending_socket.recv(1024).decode()
        reply_object = json.loads(reply)
        assert reply_object['success'] == True
        assert MY_PRIORITY_LIST.get_first() == (128, [128, 128, 128])
        assert MY_PRIORITY_LIST.size() == 1

    def test_hyperion_server_effect(self, decoder, sending_socket):
        """ Check that decoder answers to the effect command and put the
        right item in the priority_list"""
        message = {
            'command':'effect',
            'priority':128,
            'effect':{
                'name':"Rainbow.py"
            }
        }
        sending_socket.send(json.dumps(message).encode())
        reply = sending_socket.recv(1024).decode()
        reply_object = json.loads(reply)
        assert reply_object['success'] == True
        assert MY_PRIORITY_LIST.get_first() == (128, "Rainbow.py")
        assert MY_PRIORITY_LIST.size() == 1

    def test_hyperion_server_clear(self, decoder, sending_socket):
        """ Check that decoder answer to the clear command and actually
        remove the item from list """
        # Add a command to the server
        message = {
            'command':'color',
            'priority':128,
            'color':[128, 128, 128]
        }
        sending_socket.send(json.dumps(message).encode())

        message = {
            'command':'clear',
            'priority':128
        }
        # Create new socket, the previous one must be closed
        new_sending_socket = socket.create_connection(("localhost", 19444))
        new_sending_socket.send(json.dumps(message).encode())
        reply = new_sending_socket.recv(1024).decode()
        new_sending_socket.shutdown(socket.SHUT_RDWR)
        new_sending_socket.close()
        reply_object = json.loads(reply)
        assert reply_object['success'] == True
        assert MY_PRIORITY_LIST.size() == 0

    def test_hyperion_server_clear_all(self, decoder):
        """ Check that decoder answer to the clearall command and actually
        remove items from list """
        # Add commands to the server
        for i in [1, 128, 255]:
            sending_socket = socket.create_connection(("localhost", 19444))
            message = {
                'command':'color',
                'priority':i,
                'color':[i, i, i]
            }
            sending_socket.send(json.dumps(message).encode())
            sending_socket.shutdown(socket.SHUT_RDWR)
            sending_socket.close()

        sending_socket = socket.create_connection(("localhost", 19444))
        message = {
            'command':'effect',
            'priority':64,
            'effect':{
                'name': 'Rainbow.py'
            }
        }
        sending_socket.send(json.dumps(message).encode())
        sending_socket.shutdown(socket.SHUT_RDWR)
        sending_socket.close()

        sending_socket = socket.create_connection(("localhost", 19444))
        message = {
            'command':'clearall',
        }
        sending_socket.send(json.dumps(message).encode())
        reply = sending_socket.recv(1024).decode()
        sending_socket.shutdown(socket.SHUT_RDWR)
        sending_socket.close()
        reply_object = json.loads(reply)
        assert reply_object['success'] == True
        assert MY_PRIORITY_LIST.size() == 0

