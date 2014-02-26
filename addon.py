#! /usr/bin/env python

import socket
import time
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
    
    # Create the telnet connection to boblightd in an other thread
    clientThread = BoblightClient.BoblightClient(
        prioritiesList,
        settings['boblightdAddress'],
        settings['boblightdPort'])
    clientThread.daemon = True
    clientThread.start()

    # Start listening on server socket
    serverThread = HyperionDecoder.HyperionDecoder(
        prioritiesList,
        settings['listeningAddress'],
        settings['listeningPort'])
    serverThread.daemon = True
    serverThread.start()

    try:
        while serverThread.isAlive() and clientThread.isAlive():
            time.sleep(1)
    except:
        utils.log_info('Main : exiting')

if __name__ == '__main__':
    main()