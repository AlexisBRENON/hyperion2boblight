import threading
import json
import utils
import socket

class HyperionDecoder(threading.Thread):
    """Thread to interpret hyperion command"""
    def __init__(self, prioritiesList, listeningAddress, listeningPort):
        super(HyperionDecoder, self).__init__()
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.serverSocket.bind((listeningAddress, listeningPort))
        self.serverSocket.listen(5)
        self.prioritiesList = prioritiesList
        utils.log_info('Server socket initialized.')

    def run(self):
        """ Read commands, and handle it, saving informations in the shared
        priority queue """
        utils.log_info('Server socket listening.')
        while True:
            connection, clientAddress = self.serverSocket.accept()
            # Read the command (hyperion commands are shorts < 1024B)
            data = connection.recv(1024)
            if data:
                # Parse and handle command
                rqst = json.loads(data)
                command = rqst['command']
                if command == 'serverinfo':
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
                    utils.log_error('Command not recognized : %s' % (command))
                    rply = {'success':False}
                connection.send(json.dumps(rply)+'\n')
            else:
                utils.log_error('No data received...')
            connection.close()
        utils.log_error('Server socket closed unexpectedly.')

    def handle_server_info(self, rqst):
        rply = {
            'success':True,
            'info':{
                'effects':[{
                    'name':'Rainbow',
                    'script':'Rainbow.py',
                    'args':{}
                }],
                'priorities':self.prioritiesList.getPriorities(),
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
        return rply

    def handle_color(self, rqst):
        self.prioritiesList.set(int(rqst['priority']), rqst['color'])
        return {'success':True}

    def handle_effect(self, rqst):
        self.prioritiesList.set(int(rqst['priority']), rqst['effect']['name'])
        return {'success':True}

    def handle_clear(self, rqst):
        self.prioritiesList.remove(int(rqst['priority']))
        return {'success':True}

    def handle_clearall(self, rqst):
        self.prioritiesList.clear()
        return {'success':True}

