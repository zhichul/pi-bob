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

    def __init__(self,fric_upper=4,fric_lower=2,gas_acc=16,turn_acc=10,brake_acc=16,turn_radius=2,turn_mode=TURN_ANGULAR_ACCELERATION):
        self.speed = (0,0)  # vector (left_speed, right_speed)
        self.vec = (0,0)  # velocity, angular_speed
        self.gacc = gas_acc  # gas acceleration
        self.tacc = turn_acc  # angular acceleration, best be a divisor of 30
        self.bacc = brake_acc  # brake acceleration
        self.fric_upper = fric_upper  # friction acceleration upper bound
        self.fric_lower = fric_lower  # friction acceleration lower bound
        self.tradius = turn_radius # how many times of the car width
        self.k = 100
        self.max_angle = 30
        self.turn_mode = turn_mode
        self.req_shutdown = False
        self.started = False

        self.gased = False
        self.lefted = False
        self.righted = False
        self.braked = False
        self.stopped = False

    # *** update functions *** #
    def update(self):
        l,r = self.speed
        v,a = self.vec
        self.wlock.acquire()
        gased = self.gased
        lefted = self.lefted
        righted = self.righted
        braked = self.braked
        stopped = self.stopped
        self.wlock.release()

        #  overwrite if stop
        if (stopped):
            self.speed = (0,0)
            self.vec = (0,0)
            self.refresh()
            return self.speed

        # *** normal case *** #
        a = self.new_angular_velocity(a,lefted,righted)

        v = self.new_velocity(v,gased,braked,a)

        # turning
        if self.turn_mode == TURN_CONSTANT_RADIUS:
            l,r = self.turn_constant_radius(v,a)
        elif self.turn_mode == TURN_ANGULAR_ACCELERATION:
            l,r = self.turn_angular_acceleration(v,a)

        self.speed = (int(l),int(r))
        self.vec = (int(v), int(a))
        self.refresh()
        return self.speed

    def fric(self,v):
        return int(self.fric_lower+ v / 255 * (self.fric_upper -self.fric_lower))

    def new_angular_velocity(self,a,lefted,righted):
        # update angular velocity
        if righted:
            if (a > 0): a = 0
            a += -1 * self.tacc
        elif lefted:
            if (a < 0): a = 0
            a += self.tacc
        else:
            a = 0
        # elif a == 0:
        #     pass
        # elif a > 0:
        #     # no turning, apply friction
        #     a += -1 * self.tacc
        # elif a < 0:
        #     a += self.tacc

        # cut overmax
        if a == 0: pass
        elif a > self.max_angle:
            a = self.max_angle
        elif a < -1 * self.max_angle:
            a = -1 * self.max_angle

        return a

    def new_velocity(self,v,gased,braked,a):
        # get acceleration / deceleration
        acc = 0
        if gased:
            acc = self.gacc
        elif braked:
            acc = -1 * self.bacc

        # apply friction and acceleration to velocity
        if acc == 0:
            if v > 0:
                v = v - self.fric(v) if v - self.fric(v) > 0 else 0
            elif v < 0:
                v = v + self.fric(v) if v + self.fric(v) < 0 else 0
        else:
            # acc != 0
            if v > 0:
                v += -1 * self.fric(v) + acc
            elif v < 0:
                v += self.fric(v) + acc
            else:
                if acc > 0:
                    v += -1 * self.fric(v) + acc
                elif acc < 0:
                    v += self.fric(v) + acc

        # cut overmax
        if a == 0:
            max_velocity = 255
        else:
            max_velocity = self.max_velocity(a)
        if v == 0:
            pass
        elif v > max_velocity:
            v = max_velocity
        elif v < -1 * max_velocity:
            v = -1 * max_velocity
        return v

    def max_velocity(self,a):
        if self.turn_mode == TURN_ANGULAR_ACCELERATION:
            return int(255 - self.k * math.tan(abs(a / 180 * math.pi) / 2))
        elif self.turn_mode == TURN_CONSTANT_RADIUS:
            return int(255 * (self.tradius) / (self.tradius + 0.5))

    def turn_constant_radius(self,v,a):
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
            l = r = v  # no turning
        return l,r

    def turn_angular_acceleration(self,v,a):
        turn_correction = self.k * math.tan(abs(a / 180 * math.pi) / 2)
        if a > 0:
            l = v - turn_correction
            r = v + turn_correction
        elif a < 0:
            l = v + turn_correction
            r = v - turn_correction
        else:
            l = r = v  # no turning
        return l,r

    def refresh(self):
        self.wlock.acquire()
        self.gased = False
        self.braked = False
        self.lefted = False
        self.righted = False
        self.stopped = False
        self.wlock.release()

    # *** Elementary operations *** #
    def gas(self):
        if self.gased: return
        self.wlock.acquire()
        self.braked = False
        self.gased = True
        self.wlock.release()

    def left(self):
        if self.lefted: return
        self.wlock.acquire()
        self.righted = False
        self.lefted = True
        self.wlock.release()

    def right(self):
        if self.righted: return
        self.wlock.acquire()
        self.lefted = False
        self.righted = True
        self.wlock.release()

    def stop(self):
        if self.stopped: return
        self.wlock.acquire()
        self.stopped = True
        self.wlock.release()

    def brake(self):
        if self.braked: return
        self.wlock.acquire()
        self.gased = False
        self.braked = True
        self.wlock.release()

    # *** routine *** #
    def update_speed(self,proxy):
        vec = self.update()
        proxy.set_speed(vec[0],vec[1])
        # motor1(vec[0] > 0,abs(vec[0]));
        # motor2(vec[1] > 0,abs(vec[1]));

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
