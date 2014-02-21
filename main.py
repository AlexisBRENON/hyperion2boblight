#! /usr/bin/env python

import socket
import ClientThread as ct

HOST = '0.0.0.0'
PORT = 19444
priorities = []

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(5)

    try:
        while True:
            connection, clientAddress = serverSocket.accept()
            clientThread = ct.ClientThread(connection, clientAddress)
            clientThread.start()
    except KeyboardInterrupt, e:
        serverSocket.close()

if __name__ == '__main__':
    main()