import threading
import json

class HyperionDecoder(threading.Thread):
    """Thread to interpret hyperion command"""
    def __init__(self, connection, clientAddress, prioritizeList):
        super(HyperionDecoder, self).__init__()
        self.connection = connection
        self.clientAddress = clientAddress
        self.prioritizeList = prioritizeList
        print('New client connected : %s' % {clientAddress})

    def run(self):
        data = self.connection.recv(1024)
        if data:
            rqst = json.loads(data)
            command = rqst['command']
            if command == 'serverinfo':
                rply = self.handle_server_info(rqst)
                self.connection.send(json.dumps(rply)+'\n')
            elif command == 'color':
                rply = self.handle_color(rqst)
                self.connection.send(json.dumps(rply)+'\n')
            elif command == 'effect':
                rply = self.handle_effect(rqst)
                self.connection.send(json.dumps(rply)+'\n')
            else:
                print "Command not recognized : %s" % {command}
        else:
            print 'No data received...'
        self.connection.close()

    def handle_server_info(self, rqst):
        print('Received : Server info')
        rply = {}
        rply['success'] = True
        info = {}
        info['effects'] = [{
            'name':'Mood',
            'script':'mood.py',
            'args':{}
        }]
        with self.prioritizeList.lock:
            info['priorities'] = self.prioritizeList.priorities.keys()
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

    def handle_color(self, rqst):
        print('Received : color') 
        print int(rqst['priority'])
        print rqst['color']
        with self.prioritizeList.lock:
            self.prioritizeList.priorities[int(rqst['priority'])] = rqst['color']
        self.prioritizeList.event.set()
        return {'success':True}

    def handle_effect(self, rqst):
        print('Received : effect')
        print int(rqst['priority'])
        print rqst['effect']['name']
        with self.prioritizeList.lock:
            self.prioritizeList.priorities[int(rqst['priority'])] = rqst['effect']['name']
        self.prioritizeList.event.set()
        return {'success':True}

