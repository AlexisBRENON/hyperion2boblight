"""
Threaded TCP Server to handle Hyperion clients connections
"""

import json
import logging
from socketserver import ThreadingTCPServer, StreamRequestHandler

class HyperionServer(ThreadingTCPServer):
    """ Threaded TCP Server waiting for hyperion client connections.

    This server will handle request from hyperion clients and launch a HyperionRequestHandler to
    process it.
    """

    def __init__(self, server_address, priority_list):
        """
        server_address: (host, port) on which to bind the server
        priority_list: shared PriorityList which will contain commands
        """
        self.allow_reuse_address = True
        super(HyperionServer, self).__init__(server_address, HyperionRequestHandler)
        self.priority_list = priority_list

class HyperionRequestHandler(StreamRequestHandler):
    """
    The class which will be instantiated for any new connection on the server to process the
    request.
    """

    def setup(self):
        super(HyperionRequestHandler, self).setup()
        self.hyperion_priority_list = self.server.priority_list
        self.logger = logging.getLogger("HyperionRequestHandler")

    def handle(self):
        # Read data until the connection is closed
        while True:
            # Read a full line of data
            # TODO: check that this is a good way to separate commands
            data = str(self.rfile.readline(), 'utf-8').strip()
            if data:
                # Parse and handle command
                self.rqst = json.loads(data)
                command = self.rqst['command']
                rply = None
                try:
                    # Call the right command handler
                    rply = self.handlers[command](self)
                except IndexError:
                    self.logger.warning('Command not recognized : %s', command)
                    rply = self.handlers['error'](self)
                self.wfile.write(
                    bytes(json.dumps(rply) + '\n', 'utf-8'))
            else:
                # If there is no more data (connection closed), quit this handler
                break

    def _quit(self):
        """
        Tell to all the actors to quit

        TODO: is it necessary? Is there another way to achieve the same thing.
        """
        self.server.shutdown()
        self.hyperion_priority_list.put(0, 'quit')
        return {'success': True}

    def _server_info(self):
        """
        Return Hyperion server informations

        Currently returned info are:
          * effects list (hard coded)
          * list of priorities
          * transformation values (hard coded)

        TODO:
          * Improve server to handle effect discovery
          * Improve server to actually use transformation
        """
        self.logger.debug('serverinfo')
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
        priorities = self.hyperion_priority_list.get_priorities()
        for priority in priorities:
            rply['info']['priorities'].append({'priority':priority})
        return rply

    def _color(self):
        """
        Add a simple color to the priority list.
        """
        self.logger.debug(
            'color[%s]=%s',
            self.rqst['priority'],
            self.rqst['color']
        )
        self.hyperion_priority_list.put(
            int(self.rqst['priority']),
            self.rqst['color']
        )
        return {'success':True}

    def _effect(self):
        """
        Add an effect to the priority list.

        TODO:
          * handle effect options
        """
        self.logger.debug(
            'effect[%s]=%s',
            self.rqst['priority'],
            self.rqst['effect']['name']
        )
        self.hyperion_priority_list.put(
            int(self.rqst['priority']),
            self.rqst['effect']['name']
        )
        return {'success':True}

    def _clear(self):
        """
        Remove the command with the right priority from the priority list.
        """
        self.logger.debug(
            'clear[%s]',
            self.rqst['priority']
        )
        self.hyperion_priority_list.remove(int(self.rqst['priority']))
        return {'success':True}

    def _clearall(self):
        """
        Remove all items in the priority list.
        """
        self.logger.debug('clearall')
        self.hyperion_priority_list.clear()
        return {'success':True}

    def _error(self):
        """ Just return the classic error message to the client. """
        return {'success': False}

    handlers = {
        'quit': _quit,
        'serverinfo': _server_info,
        'color': _color,
        'effect': _effect,
        'clear': _clear,
        'clearall': _clearall,
        'error': _error
    }

