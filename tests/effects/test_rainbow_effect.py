import pytest
import socket
import hyperemote2boblight.lib.boblight_client as boblight_client
import hyperemote2boblight.lib.priority_list as priority_list

my_priority_list = priority_list.PriorityList()

class TestRainbowEffect:

  @pytest.fixture(scope='module')
  def server(self, request):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind(("localhost", 19444))
    server_socket.listen(5)
    def end():
      server_socket.close()
    request.addfinalizer(end)
    return server_socket

  @pytest.fixture(scope='module')
  def client(self, request):
    client = boblight_client.BoblightClient(
      getattr(request.module, "my_priority_list", None),
      "localhost", 19444)
    def end():
      my_priority_list.put(0, "Exit")
    request.addfinalizer(end)
    client.start()
    return client

  @pytest.fixture(scope='module')
  def connection(self, request, server, client):
    connection, address = server.accept()
    assert connection.recv(1024).decode() == "hello\n"
    return connection

  def test_rainbow_effect(self, connection):
    my_priority_list.put(1, 'Rainbow')
    # Receive the priority
    connection.recv(1024)
    first_color_message = connection.recv(1024).decode()
    message = ""
    # Wait a full iteration of the effect
    while message.find(first_color_message) < 0:
      message = message + connection.recv(1024).decode()
    my_priority_list.clear()
    # The message must contains command to light every rainbow color
    assert message.find("rgb %f %f %f" % (1., 0., 0.)) != -1 # Red
    assert message.find("rgb %f %f %f" % (1., 1., 0.)) != -1 # Yellow
    assert message.find("rgb %f %f %f" % (0., 1., 0.)) != -1 # Green
    assert message.find("rgb %f %f %f" % (0., 1., 1.)) != -1 # Turquoise
    assert message.find("rgb %f %f %f" % (0., 0., 1.)) != -1 # Blue
    assert message.find("rgb %f %f %f" % (1., 0., 1.)) != -1 # Purple