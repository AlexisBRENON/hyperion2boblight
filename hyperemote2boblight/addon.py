""" Main module.
It parses configuration and launches every thread implied
in this protocol transcription.
"""
#! /usr/bin/env python

import time
import hyperemote2boblight.lib.priority_list as priority_list
import hyperemote2boblight.lib.hyperion_decoder as hyperion_decoder
import hyperemote2boblight.lib.boblight_client as boblight_client

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
    # Get the priorities
    settings = get_settings()

    # Create the priority queue
    priorities_list = priority_list.PriorityList()

    # Create the telnet connection to boblightd in an other thread
    client_thread = boblight_client.BoblightClient(
        priorities_list,
        settings['boblightAddress'],
        settings['boblightPort'])
    client_thread.daemon = True
    client_thread.start()

    # Start listening on server socket
    server_thread = hyperion_decoder.HyperionDecoder(
        priorities_list,
        settings['listeningAddress'],
        settings['listeningPort'])
    server_thread.daemon = True
    server_thread.start()

    while server_thread.isAlive() and client_thread.isAlive():
        time.sleep(1)

    print('Main : exiting')

if __name__ == '__main__':
    main()
