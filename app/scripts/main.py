#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from naoqi import ALProxy
#import ssl:
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

        # Useful when you're not getting any response:
        # self.wfile.write('Hello world!')
        # return
        
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
            params = self.request_body
            async = params['async'] if ('async' in params) else True
            proxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
            proxyMethod = proxy.post.angleInterpolationWithSpeed if async else proxy.angleInterpolationWithSpeed
            method(params, proxy, proxyMethod, async)
            return

    def bound(self, value, min_value, max_value):
        result = min(value, max_value)
        result = max(result, min_value)
        return result

    def handle_motionTargets_head(self, params, proxy, proxyMethod, async):
        left_right = self.head_bound_left_right(params['left-right'])
        left_right_radians = math.radians(left_right)
        up_down = self.head_bound_up_down(params['up-down'], left_right)
        up_down_radians = math.radians(up_down)
        speed = params['speed'] if ('speed' in params) else 1.0
        proxy.setStiffnesses("Head", 1.0)
        proxyMethod( ["HeadYaw", "HeadPitch"], 
            [left_right_radians, up_down_radians], speed)
        verb = 'moving' if async else 'moved'
        self.wfile.write('Head ' + verb + ' to ' + 
            str([left_right, up_down, speed]))

    def head_bound_left_right(self, left_right):
        return self.bound(left_right, -119.5, 119.5)

    def head_bound_up_down(self, up_down, left_right):
        #return self.bound(up_down, -38.5, 29.5)
        bounds = [
            [-119.52, -25.73, 18.91],
            [ -87.49, -18.91, 11.46],
            [ -62.45, -24.64, 17.19],
            [-51.74, -27.5,  18.91 ],
            [-43.32, -31.4,  21.2  ],
            [-27.85, -38.5,  24.18 ],
            [  0,    -38.5,  29.51 ],
            [ 27.85, -38.5,  24.18 ],
            [ 43.32, -31.4,  21.2  ],
            [ 51.74, -27.5,  18.91 ],
            [ 62.45, -24.64, 17.19 ],
            [ 87.49, -18.91, 11.46 ],
            [119.52, -25.73, 18.91 ]
            ]
        for b in bounds:
            last_b = b
            if (left_right <= b[0]):
                return self.bound(up_down, b[1], b[2])
        return self.bound(up_down, last_b[1], last_b[2])

    def handle_motionTargets_left_shoulder(self, params, proxy, proxyMethod, async):
        left_right = self.bound(params['left-right'], -18, 76)
        left_right_radians = math.radians(left_right)
        up_down = self.bound(params['up-down'], -119.5, 119.5)
        up_down_radians = math.radians(up_down)
        speed = params['speed'] if ('speed' in params) else 1.0
        proxyMethod(["LShoulderRoll", "LShoulderPitch"], 
            [left_right_radians, up_down_radians], speed)
        verb = 'moving' if async else 'moved'
        self.wfile.write('(Left shoulder ' + verb + ' to ' + 
            str([left_right, up_down, speed]) + ')')

    def handle_motionTargets_right_shoulder(self, params, proxy, proxyMethod, async):
        left_right = self.bound(params['left-right'], -76, 18)
        left_right_radians = math.radians(left_right)
        up_down = self.bound(params['up-down'], -119.5, 119.5)
        up_down_radians = math.radians(up_down)
        speed = params['speed'] if ('speed' in params) else 1.0
        proxyMethod( ["RShoulderRoll", "RShoulderPitch"], 
            [left_right_radians, up_down_radians], speed)
        verb = 'moving' if async else 'moved'
        self.wfile.write('(Right shoulder ' + verb + ' to ' + 
            str([left_right, up_down, speed]) + ')')

    def handle_motionTargets_left_elbow(self, params, proxy, proxyMethod, async):
        in_out = self.bound(params['in-out'], 2, 88.5)
        in_out_radians = math.radians(in_out)
        speed = params['speed'] if ('speed' in params) else 1.0
        if ('yaw' in params):
            yaw = self.bound(params['yaw'], -119.5, 119.5)
            yaw_radians = math.radians(yaw)
            proxyMethod(
                ["LElbowRoll", "LElbowYaw"], [-in_out_radians, yaw_radians], speed)
            verb = 'moving' if async else 'moved'
            self.wfile.write('(Left elbow ' + verb + ' to ' + 
                str([in_out, yaw, speed]) + ')')
        else:
            proxyMethod(
                ["LElbowRoll"], [-in_out_radians], speed)
            verb = 'moving' if async else 'moved'
            self.wfile.write('(Left elbow ' + verb + ' to ' + 
                str([in_out, speed]) + ')')

    def handle_motionTargets_right_elbow(self, params, proxy, proxyMethod, async):
        in_out = self.bound(params['in-out'], 2, 88.5)
        in_out_radians = math.radians(in_out)
        speed = params['speed'] if ('speed' in params) else 1.0
        if ('yaw' in params):
            yaw = self.bound(params['yaw'], -119.5, 119.5)
            yaw_radians = math.radians(yaw)
            proxyMethod(
                ["RElbowRoll", "RElbowYaw"], [in_out_radians, yaw_radians], speed)
            verb = 'moving' if async else 'moved'
            self.wfile.write('(Right elbow ' + verb + ' to ' + 
                str([in_out, yaw, speed]) + ')')
        else:
            proxyMethod(
                ["RElbowRoll"], [in_out_radians], speed)
            verb = 'moving' if async else 'moved'
            self.wfile.write('(Right elbow ' + verb + ' to ' + 
                str([in_out, speed]) + ')')

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
        async = params['async'] if ('async' in params) else True
        proxyMethod = motionProxy.post.moveTo if async else motionProxy.moveTo
        proxyMethod(distance_x, distance_y, angle_radians)
        verb = 'Walking' if async else 'Walked'
        self.wfile.write('(' + verb + ' to ' + str([distance_x, distance_y, params['angle']]) + ')')

    def handle_behaviors_talks(self, params):
        message = str(params['message'])
        is_animated = params['animated'] if ('animated' in params) else False
        async = params['async'] if ('async' in params) else True
        if is_animated:
            speechProxy = ALProxy("ALAnimatedSpeech", NAO_IP, PROXY_PORT)
        else:
            speechProxy = ALProxy("ALTextToSpeech", NAO_IP, PROXY_PORT)
        proxyMethod = speechProxy.post.say if async else speechProxy.say
        proxyMethod(message)
        verb = 'Saying ' if async else 'Said '
        suffix = ' animatedly' if is_animated else ''
        description = '(' + verb + ' "' + message + '"' + suffix + ')'
        self.wfile.write(description)

    def handle_behaviors_postures(self, params):
        posture = str(params['posture'])
        speed = params['speed'] if ('speed' in params) else 1.0
        if (posture == 'CrouchStraightArms'):
            proxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
            proxyMethodAsync = proxy.post.angleInterpolationWithSpeed 
            proxyMethodSync = proxy.angleInterpolationWithSpeed
            async = False
            self.handle_behaviors_postures({'posture': 'Crouch', 'async': False})
            self.handle_motionTargets_right_shoulder({'left-right': -30, 'up-down': 90, 'speed': speed, 'async': True  }, proxy, proxyMethodAsync, True)
            self.handle_motionTargets_left_shoulder({ 'left-right':  30, 'up-down': 90, 'speed': speed, 'async': False }, proxy, proxyMethodSync, False)
            self.handle_motionTargets_right_elbow({'in-out': 0, 'speed': speed, 'async': True }, proxy, proxyMethodAsync, True)
            self.handle_motionTargets_left_elbow({ 'in-out': 0, 'speed': speed, 'async': False }, proxy, proxyMethodSync, False)
            self.handle_motionTargets_right_shoulder({'left-right': 0, 'up-down': 90, 'speed': speed, 'async': True  }, proxy, proxyMethodAsync, True)
            self.handle_motionTargets_left_shoulder({ 'left-right': 0, 'up-down': 90, 'speed': speed, 'async': False }, proxy, proxyMethodSync, False)
        else:
            async = params['async'] if ('async' in params) else True
            postureProxy = ALProxy("ALRobotPosture", NAO_IP, PROXY_PORT)
            proxyMethod = postureProxy.post.goToPosture if async else postureProxy.goToPosture
            proxyMethod(posture, speed)
        verb = 'Assuming ' if async else 'Assumed '
        self.wfile.write('(' + verb + 'posture ' + posture + ' at speed ' + str(speed) + ')')

    def handle_behaviors_awakes(self, params):
        is_awake = params['awake']
        motionProxy = ALProxy("ALMotion", NAO_IP, PROXY_PORT)
        if is_awake:
            motionProxy.wakeUp()
            self.wfile.write('(Waking up)')
        else:
            motionProxy.rest()
            self.wfile.write('(Resting)')

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
    #Can't serve https: "Server aborted the SSL handshake"
    #server.socket = ssl.wrap_socket (server.socket, certfile='./server.pem', server_side=True)
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

