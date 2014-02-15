#! /usr/bin/env python

import socket
import json

HOST = '0.0.0.0'
PORT = 12346

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

try:
    print 'Connected by', addr
    data = conn.recv(1024)
    rqst = json.loads(data)
    print(json.dumps(rqst))
    conn.send('["success": "true"]')
    data = conn.recv(1024)
    rqst = json.loads(data)
    print(json.dumps(rqst))
finally:
    conn.close()