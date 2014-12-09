import pytest
import socket
import json
import hyperemote2boblight.lib.hyperion_decoder as hyperion_decoder
import hyperemote2boblight.lib.priority_list as priority_list

my_priority_list = priority_list.PriorityList()

class TestHyperionServer:

  @pytest.fixture(scope="module")
  def decoder(self, request):
    decoder = hyperion_decoder.HyperionDecoder(
      getattr(request.module, "my_priority_list", None),
      "localhost", 19444)
    def end():
      sending_socket = socket.create_connection(("localhost", 19444))
      message = {'command':"quit"}
      sending_socket.send(json.dumps(message).encode())
    request.addfinalizer(end)
    decoder.start()
    return decoder

  @pytest.fixture
  def sending_socket(self):
    sending_socket = socket.create_connection(("localhost", 19444))
    return sending_socket

  def test_hyperion_server_create(self, decoder):
    assert decoder != None

  def test_hyperion_server_info(self, decoder, sending_socket):
    message = {'command':'serverinfo'}
    sending_socket.send(json.dumps(message).encode())
    reply = sending_socket.recv(1024).decode()
    reply_object = json.loads(reply)
    assert reply_object['success'] == True

  def test_hyperion_server_color(self, decoder, sending_socket):
    message = {
      'command':'color',
      'priority':128,
      'color':[128, 128, 128]
    }
    sending_socket.send(json.dumps(message).encode())
    reply = sending_socket.recv(1024).decode()
    reply_object = json.loads(reply)
    assert reply_object['success'] == True
    assert my_priority_list.get_first() == (128, [128, 128, 128])

  def test_hyperion_server_effect(self, decoder, sending_socket):
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
    assert my_priority_list.get_first() == (128, "Rainbow.py")
  