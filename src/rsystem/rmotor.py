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
import math
import time

TURN_CONSTANT_RADIUS = 0
TURN_ANGULAR_ACCELERATION = 1

class two_wheel_drive():
    host = rsys.server(rsys.MOTOR_PORT)
    wlock = Lock() # write lock used by gas, left, right and brake

    def __init__(self,fric=32,gas_acc=96,turn_acc=1,brake_acc=96,turn_radius=1,turn_mode=TURN_ANGULAR_ACCELERATION):
        self.speed = (0,0)  # vector (left_speed, right_speed)
        self.vec = (0,0)  # velocity, angular_speed
        self.gacc = gas_acc  # gas acceleration
        self.tacc = turn_acc  # angular acceleration, best be a divisor of 90
        self.bacc = brake_acc  # brake acceleration
        self.fric = fric  # friction acceleration
        self.tradius = turn_radius # how many times of the car width
        self.k = 50
        self.max_angle = 60
        if self.turn_mode == TURN_ANGULAR_ACCELERATION:
            self.max_velocity = int(255 - self.k * math.tan(abs(self.max_angle/180*math.pi)/2))
        elif self.turn_mode == TURN_CONSTANT_RADIUS:
            self.max_velocity = int(255 * (self.tradius + 0.5) / (self.tradius + 1))
        self.turn_mode = turn_mode
        self.req_shutdown = False
        self.started = False

        self.gased = False
        self.lefted = False
        self.righted = False
        self.braked = False
        self.stopped = False

    def update(self):
        l,r = self.speed
        v,a = self.vec
        #  overwrite if stop
        if (self.stopped):
            self.vec = (0,0,0,0)
            self.refresh()
            return self.vec

        # *** normal case *** #

        # update angular velocity
        if self.righted:
            a += -1 * self.tacc
        elif self.lefted:
            a += self.tacc
        elif a == 0: pass
        elif a > 0:
            # no turning, apply friction
            a += -1 * self.tacc
        elif a < 0:
            a += self.tacc

        # cut overmax
        if a == 0: pass
        elif a > self.max_angle:
            l = self.max_angle
        elif a < -1 * self.max_angle:
            l = -1 * self.max_angle

        # get acceleration / deceleration
        acc = 0
        if self.gased: acc = self.gacc
        elif self.braked: acc = -1 * self.bacc

        # apply friction and acceleration to velocity
        if v > 0:
            v += -1 * self.fric + acc
        elif v < 0:
            v += self.fric + acc
        else:
            if acc > 0:
                v += -1 * self.fric + acc
            elif acc < 0:
                v += self.fric + acc
            else:
                pass
                # do nothing if acc = 0 and v = 0

        # cut overmax
        if v == 0: pass
        elif v > self.max_velocity:
            v = self.max_velocity
        elif v < -1 * self.max_velocity:
            v = -1 * self.max_velocity

        # turning
        if self.turn_mode == TURN_CONSTANT_RADIUS:
            rad = self.tradius
            slow_side_factor = ((rad - 0.5) / rad)
            fast_side_factor = ((rad + 0.5) / rad)
            if a > 0:
                l = v * slow_side_factor
                r = v * fast_side_factor
            elif a < 0:
                l = v * fast_side_factor
                r = v * slow_side_factor
            else:
                l = r = v # no turning
        elif self.turn_mode == TURN_ANGULAR_ACCELERATION:
            turn_correction = self.k * math.tan(abs(a/180*math.pi)/2)
            if a > 0:
                l = v - turn_correction
                r = v + turn_correction
            elif a < 0:
                l = v + turn_correction
                r = v - turn_correction
            else:
                l = r = v  # no turning


        self.speed = (int(l),int(r))
        self.vec = (int(v), int(a))
        self.refresh()
        return self.speed

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
