#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import urlparse
import json
import math

import socket
NAO_HOSTNAME = socket.gethostname()
NAO_IP = socket.gethostbyname(NAO_HOSTNAME)
API_PORT = 8080

class httpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.handle_REQ()
        
    def do_PUT(self):
        self.handle_REQ()

    def do_PATCH(self):
        self.handle_REQ()

    def do_POST(self):
        self.handle_REQ()

    def do_DELETE(self):
        self.handle_REQ()

    def handle_REQ(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        parsed_URL = urlparse.urlparse(self.path)
        path_parts = str(parsed_URL.path)[1:].split('/')
        if len(path_parts) < 1:
            return
        if self.command == 'PUT' or self.command == 'POST':
            self.read_body()
        root_resource = path_parts[0]
        method = getattr(self, 'handle_'+root_resource, lambda: 'nothing')
        method(path_parts[1])
        
    def read_body(self):
        body_length = int(self.headers.getheader('content-length'))
        self.request_body = json.loads(self.rfile.read(body_length))
    
    def handle_motionTargets(self, target_type):
        if self.command == 'GET':
            self.wfile.write('The GET method for ' + target_type + ' does not return anything yet')
            return
        if self.command == 'PUT':
            method = getattr(self, 'handle_motionTargets_'+target_type)
            method(self.request_body)
            return

    def handle_motionTargets_head(self, params):
        left_right_radians = math.radians(params['left-right'])
        up_down_radians = math.radians(params['up-down'])
        speed = params['speed'] if ('speed' in params) else 1.0
        self.wfile.write('speed: ' + str(speed))

    def handle_behaviors(self, behavior_type):
        self.wfile.write(target_type)

try:
    #Create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', API_PORT), httpHandler)
    print 'Started httpserver on port ' , API_PORT
    
    #Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
    
