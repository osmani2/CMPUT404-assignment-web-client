#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from email import headerregistry
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

from urllib3 import get_host

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        return urllib.parse.urlparse(url).port

    def get_host(self,url):
        return urllib.parse.urlparse(url).hostname

    def connect(self, host, port):
        print('Creating socket')
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except (socket.error, msg):
            print(f'Failed to create socket. Error code: {str(msg[0])} , Error message : {msg[1]}')
            sys.exit()
        print('Socket created successfully')

        print(f'Getting IP for {host}')
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            print ('Hostname could not be resolved. Exiting')
            sys.exit()

        print (f'Ip address of {host} is {remote_ip}')
        
        self.socket.connect((host, port))
        print (f'Socket Connected to {host} on ip {remote_ip}')

    def get_code(self, data):
        return int(data.split('\r\n')[0].split(' ')[1])

    def get_headers(self,data):
        self.sendall(data)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall().strip()
        return data

    def get_body(self, data):
        body = data.split('\r\n')
        return body[len(body)-1]
    
    def sendall(self, data):
        print("Sending payload")    
        try:
            self.socket.sendall(data.encode('utf-8'))
        except socket.error:
            print ('Send failed')
            sys.exit()
        print("Payload sent successfully")
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        try:
            port = self.get_host_port(url)
            if not port:
                port=80
            host = self.get_host(url)
            self.connect(host,port)
            
            data = f'GET / HTTP/1.0\r\nHost: {host}\r\n\r\n'

            headers = self.get_headers(data)
            code = self.get_code(headers)

            # Check if body is asking for path
            body = self.get_body(headers)
            if body=='/':
                body = urllib.parse.urlparse(url).path

            #always close at the end!
            self.close()
            return HTTPResponse(code, body)

        except Exception as e:
            print('An error occured')
            code = 500
            body = ""
        
        finally:
            #always close at the end!
            self.close()
            return HTTPResponse(code, body)

    def POST(self, url, args=None):
        try:
            port = self.get_host_port(url)
            if not port:
                port=80
            host = self.get_host(url)
            self.connect(host,port)
            
            data = f'POST / HTTP/1.0\r\nHost: {host}\r\nContent-Length: 0\r\n\r\n'

            headers = self.get_headers(data)
            code = self.get_code(headers)
            body = self.get_body(headers)

            return HTTPResponse(code, body)

        except Exception as e:
            print('An error occured')
            code = 500
            body = ""
        
        finally:
            #always close at the end!
            self.close()
            return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
