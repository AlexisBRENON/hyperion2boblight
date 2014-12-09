import threading
import json
import socket


# class HandlerThread(threading.Thread):
#   def __init__(self, prioritiesList, connection):
#     super(HandlerThread, self).__init__()
#     self.prioritiesList = prioritiesList
#     self.connection = connection
#     self.connection.settimeout(2)

#   def run(self):
#     # Read the command (hyperion commands are shorts < 1024B)
#     while True:
#       try:
#         data = self.connection.recv(1024)
#       except socket.timeout:
#         data = None
#       if data:
#         # Parse and handle command
#         rqst = json.loads(data)
#         command = rqst['command']
#         if command == 'serverinfo':
#           rply = self.handle_server_info(rqst)
#         elif command == 'color':
#           rply = self.handle_color(rqst)
#         elif command == 'effect':
#           rply = self.handle_effect(rqst)
#         elif command == 'clear':
#           rply = self.handle_clear(rqst)
#         elif command == 'clearall':
#           rply = self.handle_clearall(rqst)
#         else:
#           print('Command not recognized : %s' % (command))
#           rply = {'success':False}
#         self.connection.send(json.dumps(rply)+'\n')
#       else:
#         break
#     self.connection.close()

#   def handle_server_info(self, rqst):
#     print('%s : serverinfo' %
#       (self.__class__.__name__))
#     rply = {
#       'success':True,
#       'info':{
#         'effects':[{
#           'name':'Rainbow',
#           'script':'Rainbow.py',
#           'args':{}
#         }],
#         'priorities':[],
#         'transform':{
#           'id':'default',
#           'valueGain':1.0,
#           'saturationGain':1.0,
#           'gamma':[1.0, 1.0, 1.0],
#           'threshold':[0.0, 0.0, 0.0],
#           'whitelevel':[1.0, 1.0, 1.0],
#           'blacklevel':[0.0, 0.0, 0.0]
#         }
#       }
#     }
#     priorities = self.prioritiesList.getPriorities()
#     for p in priorities:
#       rply['info']['priorities'].append({'priority':p})
#     return rply



#   def handle_clear(self, rqst):
#     print('%s : clear[%s]' %
#       (self.__class__.__name__, rqst['priority']))
#     self.prioritiesList.remove(int(rqst['priority']))
#     return {'success':True}

#   def handle_clearall(self, rqst):
#     print('%s : clearall' %
#       (self.__class__.__name__))
#     self.prioritiesList.clear()
#     return {'success':True}


class HyperionDecoder(threading.Thread):
  """Thread to interpret hyperion command"""
  def __init__(self, prioritiesList, listeningAddress, listeningPort):
    super(HyperionDecoder, self).__init__()
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    self.serverSocket.bind((listeningAddress, listeningPort))
    self.serverSocket.listen(5)
    self.prioritiesList = prioritiesList
    print('%s : Server socket initialized.' %
      (self.__class__.__name__))

  def run(self):
    """ Read commands, and handle it, saving informations in the shared
    priority queue """
    print('%s : Server socket listening.' %
      (self.__class__.__name__))
    shutdown = False
    while not shutdown:
      try:
        connection, clientAddress = self.serverSocket.accept()
        try:
          data = connection.recv(1024).decode()
        except socket.timeout:
          data = None
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
          # elif command == 'clear':
          #   rply = self.handle_clear(rqst)
          # elif command == 'clearall':
          #   rply = self.handle_clearall(rqst)
          else:
            print('Command not recognized : %s' % (command))
            rply = {'success':False}
          connection.send(json.dumps(rply).encode())
        else:
          break
      except Exception as e:
        print(e.strerror)
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
    print(rply)
    return rply

  def handle_color(self, rqst):
    print('%s : color[%s]=%s' %
      (self.__class__.__name__, rqst['priority'], rqst['color']))
    self.prioritiesList.put(int(rqst['priority']), rqst['color'])
    return {'success':True}

  def handle_effect(self, rqst):
    print('%s : effect[%s]=%s' %
      (self.__class__.__name__, rqst['priority'], rqst['effect']['name']))
    self.prioritiesList.put(int(rqst['priority']), rqst['effect']['name'])
    return {'success':True}