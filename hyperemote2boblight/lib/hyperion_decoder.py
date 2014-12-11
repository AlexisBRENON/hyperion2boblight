import json
import socket
import threading

class HyperionDecoder(threading.Thread):
  """Thread to interpret hyperion command"""
  def __init__(self, prioritiesList, listeningAddress, listeningPort):
    super(HyperionDecoder, self).__init__()
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bind_test = 5
    binded = False
    while not binded and bind_test > 0:
      try:
        self.serverSocket.bind((listeningAddress, listeningPort))
        binded = True
      except OSError:
        bind_test = bind_test-1
        print("HyperionDecoder : binding failed... %d tries remaining." % (bind_test))
    if not binded:
      exit(-1)
    else:
      self.serverSocket.listen(5)
      self.prioritiesList = prioritiesList
      print('HyperionDecoder : Server socket initialized.')

  def run(self):
    """ Read commands, and handle it, saving informations in the shared
    priority queue """
    print('HyperionDecoder : Start listening...')
    shutdown = False
    while not shutdown:
      try:
        connection, clientAddress = self.serverSocket.accept() # Wait for a new connection
        data = connection.recv(1024).decode() # Receive the command
        if data:
          # Parse and handle command
          rqst = json.loads(data)
          command = rqst['command']
          if command == 'quit':
            shutdown = True
            rply = {'success':True}
          elif command == 'serverinfo':
            rply = self.handle_server_info(rqst)
          elif command == 'color':
            rply = self.handle_color(rqst)
          elif command == 'effect':
            rply = self.handle_effect(rqst)
          elif command == 'clear':
            rply = self.handle_clear(rqst)
          elif command == 'clearall':
            rply = self.handle_clearall(rqst)
          else:
            print('Command not recognized : %s' % (command))
            rply = {'success':False}
          connection.send(json.dumps(rply).encode())
      except Exception as e:
        print(e.strerror)
      finally:
        connection.close() # Close the connection after handling the command (one connection for one command)
    self.serverSocket.shutdown(socket.SHUT_RDWR)
    self.serverSocket.close()

  def handle_server_info(self, rqst):
    print('%s : serverinfo' %
      (self.__class__.__name__))
    rply = {
      'success':True,
      'info':{
        'effects':[{
          'name':'Rainbow',
          'script':'Rainbow.py',
          'args':{}
        }],
        'priorities':[],
        'transform':{
          'id':'default',
          'valueGain':1.0,
          'saturationGain':1.0,
          'gamma':[1.0, 1.0, 1.0],
          'threshold':[0.0, 0.0, 0.0],
          'whitelevel':[1.0, 1.0, 1.0],
          'blacklevel':[0.0, 0.0, 0.0]
        }
      }
    }
    priorities = self.prioritiesList.get_priorities()
    for p in priorities:
      print(p)
      rply['info']['priorities'].append({'priority':p})
    return rply

  def handle_color(self, rqst):
    print('HyperionDecoder : color[%s]=%s' %
      (rqst['priority'], rqst['color']))
    self.prioritiesList.put(int(rqst['priority']), rqst['color'])
    return {'success':True}

  def handle_effect(self, rqst):
    print('HyperionDecoder : effect[%s]=%s' %
      (rqst['priority'], rqst['effect']['name']))
    self.prioritiesList.put(int(rqst['priority']), rqst['effect']['name'])
    return {'success':True}

  def handle_clear(self, rqst):
    print('HyperionDecoder : clear[%s]' %
      (rqst['priority']))
    self.prioritiesList.remove(int(rqst['priority']))
    return {'success':True}

  def handle_clearall(self, rqst):
    print('HyperionDecoder : clearall')
    self.prioritiesList.clear()
    return {'success':True}
