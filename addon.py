#! /usr/bin/env python

import socket
import resources.lib.PriorityList as PriorityList
import resources.lib.HyperionDecoder as HyperionDecoder
import resources.lib.BoblightClient as BoblightClient
import resources.lib.utils as utils

settings = {
    'listeningAddress':'0.0.0.0',
    'listeningPort':19444,
    'boblightdAddress':'openelec.home',
    'boblightdPort':19333
}

def main():
    # Create the priority queue
    prioritiesList = PriorityList.PriorityList()
    utils.log_info('Priority list initialized.')
    
    # Create the telnet connection to boblightd in an other thread
    clientThread = BoblightClient.BoblightClient(
        prioritiesList,
        settings['boblightdAddress'],
        settings['boblightdPort'])
    clientThread.daemon = True
    utils.log_info('Boblight thread initialized.')
    clientThread.start()
    utils.log_info('Boblight thread launched.')

    # Start listening on server socket
    serverThread = HyperionDecoder.HyperionDecoder(
        prioritiesList,
        settings['listeningAddress'],
        settings['listeningPort'])
    serverThread.daemon = True
    utils.log_info('Hyperion thread initialized.')
    serverThread.start()
    utils.log_info('Hyperion thread launched.')

    serverThread.join()
    clientThread.join()

if __name__ == '__main__':
    main()