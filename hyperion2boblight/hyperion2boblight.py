#! /usr/bin/env python3
"""
Entry point to run a Hyperion2Boblight server
"""

import threading

from hyperion2boblight import PriorityList, BoblightClient, HyperionServer

def get_settings():
    """ Return the settings of the servers """
    result = {}
    result['listeningPort'] = 19444
    result['boblightPort'] = 19445
    result['listeningAddress'] = "localhost"
    result['boblightAddress'] = "localhost"
    return result

def main():
    """ Main function """
    # Get the settings
    settings = get_settings()

    priority_list = PriorityList()

    # Create the connection to boblightd in an other thread
    client_thread = BoblightClient(
        priority_list,
        settings['boblightAddress'],
        settings['boblightPort'])
    #client_thread.daemon = True
    client_thread.start()

    # Start listening on server socket
    server = HyperionServer(
        (settings['listeningAddress'], settings['listeningPort']),
        priority_list
    )
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    server_thread.join()
    client_thread.join()

    print('Main : exiting')

if __name__ == '__main__':
    main()
