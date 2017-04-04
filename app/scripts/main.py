#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from naoqi import ALProxy
import urlparse
import json
import math
# The following are ready for the kick code:
import motion
import time
import almath

import socket
NAO_HOSTNAME = socket.gethostname()
NAO_IP = socket.gethostbyname(NAO_HOSTNAME)
API_PORT = 8080
PROXY_PORT = 9559

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

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-type, Authorization')
        self.end_headers()
        
    def handle_REQ(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            parsed_URL = urlparse.urlparse(self.path)
            path_parts = str(parsed_URL.path)[1:].split('/')
            if len(path_parts) < 1:
                return
            if (self.command == 'POST') or (self.command == 'PUT'):
                self.read_body()
            root_resource = path_parts[0]
            method = getattr(self, 'handle_'+root_resource, lambda: 'nothing')
            method(path_parts[1])
        except Exception, e:
            self.wfile.write('Exception: ' + str(e))
        
    def read_body(self):
        body_length = int(self.headers.getheader('content-length'))
        self.request_body = json.loads(self.rfile.read(body_length))
    
    def handle_motionTargets(self, target_type):
        if self.command == 'GET':
            self.wfile.write('The GET method for ' + target_type + ' does not return anything yet')
            return
        if self.command == 'PUT':
            method = getattr(self, 'handle_motionTargets_'+target_type.replace('-', '_'))
            method(self.request_body)
            return

    def bound(self, value, min_value, max_value):
        result = min(value, max_value)
        result = max(value, min_value)
        return result

    def handle_motionTargets_head(self, params):
        left_right = self.head_bound_left_right(params['left-right'])
        left_right_radians = math.radians(left_right)
        up_down = self.head_bound_up_down(params['up-down'], left_right)
        up_down_radians = math.radians(up_down)
        speed = params['speed'] if ('speed' in params) else 1.0
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        motionProxy.setStiffnesses("Head", 1.0)
        motionProxy.angleInterpolationWithSpeed(
            ["HeadYaw", "HeadPitch"], [left_right_radians, up_down_radians], speed)
        self.wfile.write('Head moving to ' + 
            str([params['left-right'], params['up-down'], speed]))

    def head_bound_left_right(self, left_right):
        return self.bound(left_right, -119.5, 119.5)

    def head_bound_up_down(self, up_down, left_right):
        return self.bound(up_down, -38.5, 29.5)

    def handle_motionTargets_left_arm(self, params):
        left_right_radians = math.radians(self.bound(params['left-right'], -18, 76))
        up_down_radians = math.radians(self.bound(params['up-down'], -119.5, 119.5))
        speed = params['speed'] if ('speed' in params) else 1.0
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        motionProxy.post.angleInterpolationWithSpeed(
            ["LShoulderRoll", "LShoulderPitch"], [left_right_radians, up_down_radians], speed)
        self.wfile.write('Left arm moving to ' + 
            str([params['left-right'], params['up-down'], speed]))

    def handle_motionTargets_right_arm(self, params):
        left_right_radians = math.radians(self.bound(params['left-right'], -76, 18))
        up_down_radians = math.radians(self.bound(params['up-down'], -119.5, 119.5))
        speed = params['speed'] if ('speed' in params) else 1.0
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        motionProxy.post.angleInterpolationWithSpeed(
            ["RShoulderRoll", "RShoulderPitch"], [left_right_radians, up_down_radians], speed)
        self.wfile.write('Right arm moving to ' + 
            str([params['left-right'], params['up-down'], speed]))

    def handle_behaviors(self, behavior_type):
        if self.command == 'GET':
            self.wfile.write('The GET method for ' + behavior_type + ' does not return anything yet')
            return
        if self.command == 'POST':
            method = getattr(self, 'handle_behaviors_'+behavior_type)
            method(self.request_body)
            return
        if self.command == 'DELETE':
            self.wfile.write('The DELETE method for ' + behavior_type + ' is not implemented yet')
            return

    def handle_behaviors_walks(self, params):
        distance_x = params['distance-x']
        distance_y = params['distance-y'] if ('distance-y' in params) else 0
        angle_radians = math.radians(params['angle']) if ('angle' in params) else 0
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        motionProxy.moveInit()
        motionProxy.post.moveTo(distance_x, distance_y, angle_radians)
        self.wfile.write('Walking to ' + str([distance_x, distance_y, params['angle']]))

    def handle_behaviors_talks(self, params):
        message = str(params['message'])
        is_animated = params['animated'] if ('animated' in params) else False
        if is_animated:
            speechProxy = ALProxy("ALAnimatedSpeech", NAO_IP, PROXY_PORT)
            description = 'Saying "' + message + '" animatedly'
        else:
            speechProxy = ALProxy("ALTextToSpeech", NAO_IP, PROXY_PORT)
            description = 'Saying "' + message + '"'
        speechProxy.post.say(message)
        self.wfile.write(description)

    def handle_behaviors_postures(self, params):
        posture = str(params['posture'])
        speed = params['speed'] if ('speed' in params) else 1.0
        postureProxy = ALProxy("ALRobotPosture", NAO_IP, PROXY_PORT)
        postureProxy.post.goToPosture(posture, speed)
        self.wfile.write('Assuming posture ' + posture + ' at speed ' + str(speed))

    def handle_behaviors_awakes(self, params):
        is_awake = params['awake']
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        if is_awake:
            motionProxy.wakeUp()
            self.wfile.write('Waking up')
        else:
            motionProxy.rest()
            self.wfile.write('Resting')

    def handle_behaviors_kicks(self, params):
        postureProxy = ALProxy("ALRobotPosture", NAO_IP, PROXY_PORT)
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)

       # Activate Whole Body Balancer
        isEnabled  = True
        motionProxy.wbEnable(isEnabled)

        # Legs are constrained fixed
        stateName  = "Fixed"
        supportLeg = "Legs"
        motionProxy.wbFootState(stateName, supportLeg)

        # Constraint Balance Motion
        isEnable   = True
        supportLeg = "Legs"
        motionProxy.wbEnableBalanceConstraint(isEnable, supportLeg)

        # Com go to LLeg
        supportLeg = "LLeg"
        duration   = 2.0
        motionProxy.wbGoToBalance(supportLeg, duration)

        # RLeg is free
        stateName  = "Free"
        supportLeg = "RLeg"
        motionProxy.wbFootState(stateName, supportLeg)

        # RLeg is optimized
        effector = "RLeg"
        axisMask = 63
        frame    = motion.FRAME_WORLD

        # Motion of the RLeg
        times   = [2.0, 2.7, 4.5]

        path = computePath(motionProxy, effector, frame)

        motionProxy.transformInterpolations(effector, frame, path, axisMask, times)

        # Example showing how to Enable Effector Control as an Optimization
        isActive     = False
        motionProxy.wbEnableEffectorOptimization(effector, isActive)

        # Com go to LLeg
        supportLeg = "RLeg"
        duration   = 2.0
        motionProxy.wbGoToBalance(supportLeg, duration)

        # RLeg is free
        stateName  = "Free"
        supportLeg = "LLeg"
        motionProxy.wbFootState(stateName, supportLeg)

        effector = "LLeg"
        path = computePath(motionProxy, effector, frame)
        motionProxy.transformInterpolations(effector, frame, path, axisMask, times)

        time.sleep(1.0)

        # Deactivate Head tracking
        isEnabled = False
        motionProxy.wbEnable(isEnabled)

try:
    #Create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', API_PORT), httpHandler)
    print 'Started httpserver on port ' , API_PORT
    
    #Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()

def computePath(proxy, effector, frame):
    dx      = 0.05                 # translation axis X (meters)
    dz      = 0.05                 # translation axis Z (meters)
    dwy     = 5.0*almath.TO_RAD    # rotation axis Y (radian)

    useSensorValues = False

    path = []
    currentTf = []
    try:
        currentTf = proxy.getTransform(effector, frame, useSensorValues)
    except Exception, errorMsg:
        print str(errorMsg)
        print "This example is not allowed on this robot."
        exit()

    # 1
    targetTf  = almath.Transform(currentTf)
    targetTf *= almath.Transform(-dx, 0.0, dz)
    targetTf *= almath.Transform().fromRotY(dwy)
    path.append(list(targetTf.toVector()))

    # 2
    targetTf  = almath.Transform(currentTf)
    targetTf *= almath.Transform(dx, 0.0, dz)
    path.append(list(targetTf.toVector()))

    # 3
    path.append(currentTf)

    return path
