import threading
import json

class ClientThread(threading.Thread):
    """Thread to interpret hyperion command"""
    def __init__(self, connection, clientAddress):
        super(ClientThread, self).__init__()
        self.connection = connection
        self.clientAddress = clientAddress
        print('New client connected : %s' % {clientAddress})

    def run(self):
        data = self.connection.recv(1024)
        if data:
            rqst = json.loads(data)
            command = rqst['command']
            if command == 'serverinfo':
                rply = self.handle_server_info(rqst)
                self.connection.send(json.dumps(rply)+'\n')
            else:
                print "Command not recognized : %s" % {command}
        else:
            print 'No data received...'
        self.connection.close()

    def handle_server_info(self, rqst):
        rply = {}
        rply['success'] = True
        info = {}
        info['effects'] = []
        # TODO : get priorities
        info['priorities'] = []
        transform = {}
        transform['blacklevel'] = [0.0, 0.0, 0.0]
        transform['gamma'] = [1.0, 1.0, 1.0]
        transform['id'] = 'default'
        transform['saturationGain'] = 1.0
        transform['threshold'] = [0.0, 0.0, 0.0]
        transform['valueGain'] = 1.0
        transform['whitelevel'] = [1.0, 1.0, 1.0]
        info['transform'] = [transform]
        rply['info'] = info
        return rply

