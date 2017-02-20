# Mid-level interface for manipulating motors
# Thread count: 2
### gopigo import start
from gopigo import *
import sys

import atexit
atexit.register(stop)
### gopigo import end

from . import rsys
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as client
from threading import Lock
from threading import Thread

class two_wheel_drive():
    host = rsys.server(rsys.MOTOR_PORT)
    wlock = Lock() # write lock used by gas, left, right and brake

    def __init__(self,fric=10,gacc=60,tacc=0.8,bacc=35):
        self.vec = (0,0) # vector (left_speed, right_speed)
        self.gacc = gacc # gas acceleration
        self.tacc = tacc # turn acceleration
        self.bacc = bacc # brake acceleration
        self.fric = fric # friction factor
        self.req_shutdown = False
        self.started = False

        self.gased = False
        self.lefted = False
        self.righted = False
        self.braked = False
        self.stopped = False
    
    def update(self):
        l,r = self.vec
        # overwrite stop
        if (self.stopped):
            self.vec = (0,0)
            self.refresh()
            return self.vec
        # normal
        lacc = 0
        racc = 0
        fric = self.fric
        if (self.gased):
            lacc = racc = self.gacc
        elif (self.braked):
            lacc = racc = -1 * self.bacc

        l = l + lacc
        r = r + racc
        
        # turning
        if (self.righted):
            l *= self.tacc
            r /= self.tacc
        elif (self.lefted):
            l /= self.tacc
            r *= self.tacc

        # friction effect
        if l > 0:
            l = l - fric if l - fric > 0 else 0
        elif l < 0:
            l = l + fric if l + fric < 0 else 0
        if r > 0:
            r = r - fric if r - fric > 0 else 0
        elif l < 0:
            r = r + fric if r + fric < 0 else 0
        
        # correction for straight deviation
        if (lacc == racc and l != r):
            l = r = l + r // 2

        # correction for overmax
        if (l > 255):
            l = 255
        elif (l < -255):
            l = -255
        if (r > 255):
            r = 255
        elif (r < -255):
            r = -255
        lacc = racc = 0
        self.vec = (int(l),int(r))
        self.refresh()
        return self.vec 
    
    def refresh(self):
        self.gased = False
        self.braked = False
        self.lefted = False
        self.righted = False
        self.stopped = False

    def gas(self):
        self.wlock.acquire()
        self.braked = False
        self.gased = True
        self.wlock.release()
    
    def left(self):
        self.wlock.acquire()
        self.righted = False
        self.lefted = True
        self.wlock.release()

    def right(self):
        self.wlock.acquire()
        self.lefted = False
        self.righted = True
        self.wlock.release()
    
    def stop(self):
        self.wlock.acquire()
        self.stopped = True
        self.wlock.release()

    def brake(self):
        self.wlock.acquire()
        self.gased = False
        self.braked = True
        self.wlock.release()

    def update_speed(self,proxy):
        vec = self.update()
        #proxy.set_speed(vec[0],vec[1])
        motor1(vec[0] > 0,abs(vec[0]));
        motor2(vec[1] > 0,abs(vec[1]));

    def start(self):
        def f():
            if (self.started): return
            self.started = True
            with client.ServerProxy(self.host) as proxy:
                while (not self.req_shutdown):
                    self.update_speed(proxy)
                    time.sleep(0.25);
            self.started = False
            self.req_shutdwon = False
        Thread(target=f).start()

    def shutdown(self):
        self.req_shutdown = True

class motor_interface():

    speed = [0,0]

    def iset_speed(self, s1, s2):
        self.speed[0] = s1
        self.speed[1] = s2
        motor1(s1 > 0,abs(s1));
        motor2(s2 > 0,abs(s2));
        return "Speed set to <%d,%d>" % (s1, s2)

    def iget_speed(self):
        return self.speed

def main():
    interface = motor_interface()
    server = SimpleXMLRPCServer(("127.0.0.1", rsys.MOTOR_PORT))
    server.register_function(interface.iget_speed,"get_speed")
    server.register_function(interface.iset_speed,"set_speed")
    server.register_function(lambda:True, "is_alive")
    print("Listening on port %d..." % rsys.MOTOR_PORT)
    server.serve_forever()
