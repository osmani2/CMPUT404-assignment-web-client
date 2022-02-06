#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Natasha Osmani
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
import json

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    '''
    Parse url for hosts port if any else uses port 80
    '''
    def get_host_port(self,url):
        port =  urllib.parse.urlparse(url).port
        if not port:
            port=80

        return port

    '''
    Parse url for host
    '''
    def get_host(self,url):
        return urllib.parse.urlparse(url).hostname

    '''
    Creates and connects socket to host
    Taken from Lab 2
    '''
    def connect(self, host, port):
        # Creat Socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except (socket.error, msg):
            print(f'Failed to create socket. Error code: {str(msg[0])} , Error message : {msg[1]}')
            sys.exit()

        # Get hosts IP
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            print ('Hostname could not be resolved. Exiting')
            sys.exit()

        # Connect socket
        self.socket.connect((host, port))

    '''
    Parse header for code
    '''
    def get_code(self, data):
        return int(data.split('\r\n')[0].split(' ')[1])

    '''
    Send data and recieve header
    '''
    def get_headers(self,data):
        self.sendall(data)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall().strip()
        return data

    '''
    Parse header for body
    '''
    def get_body(self, data):
        body = data.split('\r\n')
        return body[len(body)-1]
    
    '''
    Send all data
    '''
    def sendall(self, data):   
        try:
            self.socket.sendall(data.encode('utf-8'))
        except socket.error:
            print ('Send failed')
            sys.exit()
    '''
    Close socket connection
    '''   
    def close(self):
        self.socket.close()

    '''Read everything from the socket'''
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

    '''
    Send an HTTP GET request
    '''
    def GET(self, url, args=None):
        try:
            # get host and port
            port = self.get_host_port(url)
            host = self.get_host(url)

            # Connect socket
            self.connect(host,port)
            
            # Create and send data/request
            data = f'GET / HTTP/1.0\r\nHost: {host}\r\n\r\n'
            headers = self.get_headers(data)

            #Get the code and body from header
            code = self.get_code(headers)
            body = self.get_body(headers)

            # Check if body is for the path
            if body=='/':
                body = urllib.parse.urlparse(url).path

        except Exception as e:
            print('An error occured')
            code = 500
            body = ""
        
        finally:
            #always close at the end!
            self.close()

            # Print body to stdout
            print("BODY RECIEVED!\n",body,"\n")
            return HTTPResponse(code, body)

    '''
    Send an HTTP POST request
    '''
    def POST(self, url, args=None):
        try:
            port = self.get_host_port(url)
            host = self.get_host(url)
            self.connect(host,port)

            body = ''
            # Use args, if any, for the body
            if args is not None:
                post_args = args.copy()
                for key in post_args:
                    val =  post_args[key].split('\r\n')
                    post_args[key]=val
                body = json.dumps(post_args, indent=2).encode('utf-8')
            
            # Get length of body
            post_length = len(body)
     
            # Prep and send data
            data = f'POST / HTTP/1.0\r\nHost: {host}\r\nContent-Length:{post_length}\r\nContent-Type: application/x-www-form-urlencoded\r\n{body}\r\n\r\n'

            headers = self.get_headers(data)
            
            # Recieve Code

            # Get body returned from header
            code = self.get_code(headers)
            if args is None:
                body = self.get_body(headers)

        except Exception as e:
            print('An error occured')
            code = 500
            body = ""
        
        finally:
            #always close at the end!
            self.close()

            # Print body to stdout
            print("BODY RECIEVED!\n",body,"\n")
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
