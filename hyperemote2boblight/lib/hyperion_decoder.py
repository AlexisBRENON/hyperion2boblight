""" Hyperion decoder is a module which play a role of a Hyperion Server.
It handles hyperion commands from any client and add them to a priority list
"""
import json
import socket
import threading

class HyperionDecoder(threading.Thread):
    """Thread to interpret hyperion command"""
    def __init__(self, priorities_list, listeningAddress, listeningPort):
        super(HyperionDecoder, self).__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_test = 5
        binded = False
        while not binded and bind_test > 0:
            try:
                self.server_socket.bind((listeningAddress, listeningPort))
                binded = True
            except OSError:
                bind_test = bind_test-1
                print("HyperionDecoder : binding failed... %d tries remaining." % (bind_test))
        if not binded:
            exit(-1)
        else:
            self.server_socket.listen(5)
            self.priorities_list = priorities_list
            print('HyperionDecoder : Server socket initialized.')

    def run(self):
        """ Read commands, and handle it, saving informations in the shared
        priority queue """
        print('HyperionDecoder : Start listening...')
        shutdown = False
        while not shutdown:
            connection, _ = self.server_socket.accept() # Wait for a new connection
            try:
                data = connection.recv(1024).decode() # Receive the command
                if data:
                    # Parse and handle command
                    rqst = json.loads(data)
                    command = rqst['command']
                    if command == 'quit':
                        shutdown = True
                        rply = {'success':True}
                    elif command == 'serverinfo':
                        rply = self.handle_server_info()
                    elif command == 'color':
                        rply = self.handle_color(rqst)
                    elif command == 'effect':
                        rply = self.handle_effect(rqst)
                    elif command == 'clear':
                        rply = self.handle_clear(rqst)
                    elif command == 'clearall':
                        rply = self.handle_clearall()
                    else:
                        print('Command not recognized : %s' % (command))
                        rply = {'success':False}
                    connection.send(json.dumps(rply).encode())
            except OSError as error:
                print(error.strerror)
            finally:
                # Close the connection after handling the command (one connection for one command)
                connection.close()
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()

    def handle_server_info(self):
        """ Return the right JSON string to send to client when asking server infos """
        print('HyperionServer : serverinfo')
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
        priorities = self.priorities_list.get_priorities()
        for priority in priorities:
            rply['info']['priorities'].append({'priority':priority})
        return rply

    def handle_color(self, rqst):
        """ Add the right item to the priority list and return the JSON string to send back
        to the client when issuing a color command """
        print('HyperionDecoder : color[%s]=%s' % (
            rqst['priority'], rqst['color']))
        self.priorities_list.put(int(rqst['priority']), rqst['color'])
        return {'success':True}

    def handle_effect(self, rqst):
        """ Add the right item to the priority list and return the JSON string to send back
        to the client when issuing an effect command """
        print('HyperionDecoder : effect[%s]=%s' % (
            rqst['priority'], rqst['effect']['name']))
        self.priorities_list.put(int(rqst['priority']), rqst['effect']['name'])
        return {'success':True}

    def handle_clear(self, rqst):
        """ Remove the right item to the priority list and return the JSON string to send back
        to the client when issuing a clear command """
        print('HyperionDecoder : clear[%s]' % (
            rqst['priority']))
        self.priorities_list.remove(int(rqst['priority']))
        return {'success':True}

    def handle_clearall(self):
        """ Remove all items from the priority list and return the JSON string to send back
        to the client when issuing a clearall command """
        print('HyperionDecoder : clearall')
        self.priorities_list.clear()
        return {'success':True}
