#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from naoqi import ALProxy
import urlparse

import socket
NAO_HOSTNAME = socket.gethostname()
NAO_IP = socket.gethostbyname(NAO_HOSTNAME)
PORT_NUMBER = 8080

class httpHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        try:
            tts = ALProxy("ALTextToSpeech", NAO_IP, 9559)
            tts.say(NAO_HOSTNAME)
            tts.say(NAO_IP)
            self.wfile.write("Get a GET!")
        except Exception, e:
            self.wfile.write(str(e))
        return
        
    def do_PUT(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        try:
            o = urlparse.urlparse(self.path)
            query = urlparse.parse_qs(o.query)
            angleYaw = float(query["yaw"][0])
            anglePitch = float(query["pitch"][0])
            motion = ALProxy("ALMotion", NAO_IP, 9559)
            motion.post.angleInterpolationWithSpeed(
                ["HeadYaw", "HeadPitch"],
                [angleYaw, anglePitch],
                0.99
            )
            
            self.wfile.write(str([angleYaw, anglePitch]))
        except Exception, e:
            self.wfile.write(str(e))
        return

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), httpHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
    
    #Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
    
