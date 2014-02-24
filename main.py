#! /usr/bin/env python

import socket
import HyperionDecoder as hd
import BoblightClient as bc
import PrioritizeList as pl

HOST = '0.0.0.0'
PORT = 19444
priorities = []

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(5)
    prioritiesList = pl.PrioritizeList()
    client = bc.BoblightClient(prioritiesList, 'openelec.home', 19333)
    client.start()
    try:
        while True:
            connection, clientAddress = serverSocket.accept()
            HyperionDecoder = hd.HyperionDecoder(connection, clientAddress, prioritiesList)
            HyperionDecoder.start()
    except KeyboardInterrupt, e:
        serverSocket.close()

if __name__ == '__main__':
    main()