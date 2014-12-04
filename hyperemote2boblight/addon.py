#! /usr/bin/env python

import socket
import time
import resources.lib.PriorityList as PriorityList
import resources.lib.HyperionDecoder as HyperionDecoder
import resources.lib.BoblightClient as BoblightClient
import resources.lib.utils as utils
import xbmc, xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonicon__    = xbmc.translatePath('%s/icon.png' % __addonpath__ )
__language__     = __addon__.getLocalizedString

def getSettings():
  result = {}
  result['listeningPort'] = int(__addon__.getSetting('hyperionPort'))
  result['boblightPort'] = int(__addon__.getSetting('boblightPort'))
  if __addon__.getSetting('hyperionIsHostname') == 'true':
    result['listeningAddress'] = __addon__.getSetting('hyperionHostname')
  else:
    result['listeningAddress'] = __addon__.getSetting('hyperionIP')
  if __addon__.getSetting('boblightIsHostname') == 'true':
    result['boblightAddress'] = __addon__.getSetting('boblightHostname')
  else:
    result['boblightAddress'] = __addon__.getSetting('boblightIP')
  return result

def main():
  # Get the priorities
  settings = getSettings()
  utils.log_debug(str(settings))

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
    while serverThread.isAlive() and clientThread.isAlive() and not xbmc.abortRequested:
      time.sleep(1)
  except:
    pass
  
  utils.log_info('Main : exiting')

if __name__ == '__main__':
  main()