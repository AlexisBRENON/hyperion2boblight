import threading
import sys
import socket
import hyperemote2boblight.lib.effects.rainbow as rainbow

class BoblightClient(threading.Thread):
  """Thread which is connected to the boblight server"""
  def __init__(self, prioritiesList, serverAddress, serverPort):
    super(BoblightClient, self).__init__()
    self.prioritiesList = prioritiesList
    try:
      self.connection = socket.create_connection((serverAddress, serverPort))
    except socket.error:
      print('%s : Unable to create the Telnet connection to boblight server \'%s:%d\'' %
        (self.__class__.__name__, serverAddress, serverPort))
      sys.exit()
    self.connection.send('hello\n'.encode())
    self.lights = ['screen']
    print('%s : Boblight connection initialized.' %
      (self.__class__.__name__))

  def set_lights(self, r, g, b):
    message = ""
    for light in self.lights:
      message = message + 'set light %s rgb %f %f %f\n' % (light,
          r/255.0,
          g/255.0,
          b/255.0)
    return message

  def set_priority(self, priority):
    return 'set priority %d\n' % (priority)

  def run(self):
    stopEvent = threading.Event()
    shutdown = False
    curent_priority = 256
    while not shutdown:
      # wait for new command
      (priority, command) = self.prioritiesList.wait_new_item()
      message = ""
      # Handle the exit command whatever the priority
      if type(command) == str and command == "Exit":
        shutdown = True
        message = message + self.set_priority(0)
        message = message + self.set_lights(0, 0, 0)
      else:
        stopEvent.set()
        print('%s : Executing %s:%s' % (self, priority, command))
        # Handle classic 'color' command
        if type(command) is list:
          message = message + self.set_priority(priority)
          message = message + self.set_lights(command[0], command[1], command[2])
        # Handle rainbow effect
        elif type(command) == str and command == 'Rainbow':
          message = message + self.set_priority(priority)
          rainbow.RainbowThread(self.connection, self.lights, stopEvent).start()
        elif (priority, command) == (None, None):
          message = message + self.set_priority(0)
          message = message + self.set_lights(0, 0, 0)
        else:
          print("BoblightClient : command not recognized : %s" % (command))
      # Actually send commands to the Boblight server
      if message != "":
        self.connection.send(message.encode())
      # Loop to wait new command
    print('BoblightClient : Shutting Down')
    self.connection.shutdown(socket.SHUT_RDWR)
    self.connection.close()
    
