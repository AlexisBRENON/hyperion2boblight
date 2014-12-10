import pytest
import socket
import hyperemote2boblight.lib.boblight_client as boblight_client
import hyperemote2boblight.lib.priority_list as priority_list

my_priority_list = priority_list.PriorityList()

class TestBoblightClient:

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
    return connection


  def test_boblight_client_create(self, connection):
    received = connection.recv(1024).decode()
    assert received == "hello\n"

  def test_boblight_client_set_color(self, connection):
    my_priority_list.put(128, [128, 128, 128])
    received = connection.recv(1024).decode()
    assert received == "set priority 128\nset light screen rgb %f %f %f\n" % (128/255.0, 128/255.0, 128/255.0)
  
  def test_boblight_client_set_color_with_higher_priority(self, connection):
    my_priority_list.put(255, [255, 255, 255])
    connection.settimeout(2)
    # Adding a higher priority should not react, so no message is sent
    with pytest.raises(socket.timeout):
      received = connection.recv(1024).decode()

  def test_boblight_client_set_color_with_lower_priority(self, connection):
    my_priority_list.put(1, [1, 1, 1])
    received = connection.recv(1024).decode()
    assert received == "set priority 1\nset light screen rgb %f %f %f\n" % (1/255.0, 1/255.0, 1/255.0)

  def test_boblight_client_change_current_command(self, connection):
    my_priority_list.put(1, [11, 11, 11])
    received = connection.recv(1024).decode()
    assert received == "set priority 1\nset light screen rgb %f %f %f\n" % (11/255.0, 11/255.0, 11/255.0)

  def test_boblight_client_change_any_command(self, connection):
    my_priority_list.put(128, [64, 64, 64])
    connection.settimeout(2)
    # Changing any non first command do nothing
    with pytest.raises(socket.timeout):
      received = connection.recv(1024).decode()

  def test_boblight_client_remove(self, connection):
    my_priority_list.remove(1)
    received = connection.recv(1024).decode()
    assert received == "set priority 128\nset light screen rgb %f %f %f\n" % (64/255.0, 64/255.0, 64/255.0)