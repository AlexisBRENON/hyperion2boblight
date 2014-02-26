#! /usr/bin/env python

import socket
import time
import resources.lib.PriorityList as PriorityList
import resources.lib.HyperionDecoder as HyperionDecoder
import resources.lib.BoblightClient as BoblightClient
import resources.lib.utils as utils
import resources.lib.xbmc.xbmcaddon as xbmcaddon
import resources.lib.xbmc.xbmc as xbmc

__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonicon__    = xbmc.translatePath('%s/icon.png' % __addonpath__ )
__language__     = __addon__.getLocalizedString

#settings = getSettings()
settings = {
    'listeningAddress':'0.0.0.0',
    'listeningPort':19444,
    'boblightAddress':'openelec.home',
    'boblightPort':19333
}

def getSettings():
    result['listeningPort'] = __addon__.getSettings('hyperionPort')
    result['boblightPort'] = __addon__.getSettings('boblightPort')
    if __addon__.getSettings('hyperionIsHostname') == 'true':
        result['listeningAddress'] = __addon__.getSettings('hyperionHostname')
    else:
        result['listeningAddress'] = __addon__.getSettings('hyperionIP')
    if __addon__.getSettings('boblightIsHostname') == 'true':
        result['boblightAddress'] = __addon__.getSettings('boblightHostname')
    else:
        result['boblightAddress'] = __addon__.getSettings('boblightIP')
    return result

def main():
    # Create the priority queue
    prioritiesList = PriorityList.PriorityList()
    
    # Create the telnet connection to boblightd in an other thread
    clientThread = BoblightClient.BoblightClient(
        prioritiesList,
        settings['boblightAddress'],
        settings['boblightPort'])
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