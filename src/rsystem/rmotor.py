# Mid-level interface for manipulating motors
# Thread count: 2

from gopigo import *
import atexit

atexit.register(stop)

from . import rsys
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as client
from threading import Lock
from threading import Thread
import math
import time

"""
module constants
"""
TURN_CONSTANT_RADIUS = 0
TURN_ANGULAR_ACCELERATION = 1


class two_wheel_drive():
    """
    two_wheel_drive

    Emulates a vehicle with four actions, accelerating, decelerating, turning left and turning right.
    Simulates forces applied to the vehicle in discrete time.
    """
    host = rsys.server(rsys.MOTOR_PORT)  # address of server hosting motor communication interface
    wlock = Lock()  # Lock used by gas(), left(), right(), brake(), update(), and refresh().
    req_shutdown = False  # flag for shutting down the thread running from start()
    started = False  # flag for indicating there is already a thread running from start()
    gased = False  # signal for gas
    lefted = False  # signal for left
    righted = False  # signal for right
    braked = False  # signal for brake
    stopped = False  # signal for stop

    def __init__(self, fric_upper=4, fric_lower=2, gas_acc=16, turn_acc=10, brake_acc=16, turn_radius=2,
                 turn_mode=TURN_CONSTANT_RADIUS):
        """

        :param fric_upper: upper bound for friction [0,255]
        :param fric_lower: lower bound for friction [0,fric_upper]
        :param gas_acc: acceleration for emulating gas [0,255]
        :param turn_acc: angular acceleration for emulating turning (useful in TURN_ANGULAR_ACCELERATION mode) [0,90]
        :param brake_acc: acceleration for emulating [0,255]
        :param turn_radius: constant turn radius for emulating turning (useful in TURN_CONSTANT_RADIUS mode) [integer]
        :param turn_mode: the mode for turning emulation, a multiple of car width. Use module constants.
        """
        self.speed = (0, 0)  # (left_speed, right_speed) [-255,255] for both
        self.vec = (0, 0)  # (velocity, angular_speed) [-255,255] for velocity,
        #  [integer] for angular speed, - means right, + means left
        self.gacc = gas_acc  # gas acceleration
        self.tacc = turn_acc  # turning angular acceleration
        self.bacc = brake_acc  # brake acceleration
        self.fric_upper = fric_upper  # friction acceleration upper bound
        self.fric_lower = fric_lower  # friction acceleration lower bound
        self.tradius = turn_radius  # [integer] multiple of the car width
        self.k = 100  # constant used in TURN_ANGULAR_ACCELERATION mode
        self.max_angular = 30  # constant used for turning
        self.turn_mode = turn_mode  # turning mode

    # *** update functions *** #
    def update(self):
        """
        Called by update_speed() regularly to emulate the forces being applied to the car.
        Processes and clears gased, lefted, righted, braked, and stopped signals.
        Below are helper functions, which you can skip and look into later if necessary.
        :return: (lspeed, rspeed) [-255,255] [-255,255]
        """
        l, r = self.speed
        v, a = self.vec
        self.wlock.acquire()  # acquire lock for reading signals
        gased = self.gased
        lefted = self.lefted
        righted = self.righted
        braked = self.braked
        stopped = self.stopped
        self.wlock.release()  # release lock

        #  Stop and return if stop signal is received
        if (stopped):
            self.speed = (0, 0)
            self.vec = (0, 0)
            self.refresh()  # clear signals
            return self.speed

        # Update speeds and velocities if not stopped
        a = self.new_angular_velocity(a, lefted, righted)
        v = self.new_velocity(v, gased, braked, a)
        # Simulate turning
        if self.turn_mode == TURN_CONSTANT_RADIUS:
            l, r = self.turn_constant_radius(v, a)
        elif self.turn_mode == TURN_ANGULAR_ACCELERATION:
            l, r = self.turn_angular_acceleration(v, a)

        # Pack results into tuples
        self.speed = (int(l), int(r))
        self.vec = (int(v), int(a))
        self.refresh()  # clear signals
        return self.speed

    def fric(self, v):
        """
        Linear (to velocity) friction calculator.
        fric = fric_lower + velocity/255 * (fric_upper - fric_lower)
        :param v: velocity
        :return: the friction
        """
        return int(self.fric_lower + v / 255 * (self.fric_upper - self.fric_lower))

    def new_angular_velocity(self, a, lefted, righted):
        """
        Update angular velocity
        :param a: current
        :param lefted: True iff signaled left
        :param righted: True iff signaled right
        :return: new angular velocity
        """
        assert (lefted in {0,1} and (righted in {0,1}))
        acc_dir = -1 * lefted + 1 * righted
        if acc_dir * a < 0: a = 0 # change in turning
        # if signaled left or right, apply the forces
        a = a * abs(acc_dir) + acc_dir * self.tacc

        # if result exceeded max/min, cutoff at max/min
        if a > self.max_angular: a = self.max_angular
        elif a < -1 * self.max_angular: a = -1 * self.max_angular
        return a

    def new_velocity(self, v, gased, braked, a):
        """
        Updates velocity
        :param v: current velocity
        :param gased: True iff signaled gas
        :param braked: True iff signaled brake
        :param a: angular velocity
        :return: new velocity
        """
        assert(gased in {1,0} and braked in {1,0})

        # get acceleration / deceleration
        acc = gased * self.gacc - braked * braked

        # directions of v, acc, and friction
        v_dir = v / abs(v) if v != 0 else 0
        acc_dir = acc / abs(acc) if acc != 0 else 0
        fric_dir = -1 * v_dir if v_dir else -1 * acc_dir  # if v = 0, use opposite of acc_dir
        assert((v_dir in {-1,0,1}) and (acc_dir in {-1,0,1}) and (fric_dir in {-1, 0, 1}))

        # apply friction and acceleration to velocity
        v_new = v + acc_dir * acc + fric_dir * self.fric(v)
        if v * v_new < 0: v_new = 0  # crossing 0, force 0

        # if result exceeded max/min cutoff at max/min
        v_max = self.max_velocity(a) if a else 255
        if v_new > v_max: v_new = v_max
        elif v_new < -1 * v_max: v_new = -1 * v_max
        return v_new

    def max_velocity(self, a):
        """
        Calculates max velocity to make corrections for high speed turning
        :param a: angular velocity
        :return: the max velocity
        """
        if self.turn_mode == TURN_ANGULAR_ACCELERATION:
            return int(255 - self.k * math.tan(abs(a / 180 * math.pi) / 2))
        elif self.turn_mode == TURN_CONSTANT_RADIUS:
            return int(255 * (self.tradius) / (self.tradius + 0.5))

    def turn_constant_radius(self, v, a):
        """
        Simulates turning with a constant turning radius
        :param v: velocity
        :param a: angular velocity
        :return: left speed, right speed
        """
        rad = self.tradius
        slow_side_factor = ((rad - 0.5) / rad)
        fast_side_factor = ((rad + 0.5) / rad)
        if a > 0:
            r = v * slow_side_factor
            l = v * fast_side_factor
        elif a < 0:
            r = v * fast_side_factor
            l = v * slow_side_factor
        else:
            l = r = v  # no turning
        return l, r

    def turn_angular_acceleration(self, v, a):
        """
        Simulates turning with increasing angular velocity
        :param v: velocity
        :param a: angular velocity
        :return: left speed, right speed
        """
        turn_correction = self.k * math.tan(abs(a / 180 * math.pi) / 2)
        if a > 0:
            r = v - turn_correction
            l = v + turn_correction
        elif a < 0:
            r = v + turn_correction
            l = v - turn_correction
        else:
            l = r = v  # no turning
        return l, r

    def refresh(self):
        """
        Clears the signals
        :return:
        """
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
    def update_speed(self, proxy):
        """
        calls update to get new speeds
        :param proxy: the server containing the motor interface
        :return:
        """
        vec = self.update()
        proxy.set_speed(vec[0], vec[1])
        # motor1(vec[0] > 0,abs(vec[0])); # bypass the motor interface server and talk directly to motor
        # motor2(vec[1] > 0,abs(vec[1])); # for testing

    def start(self):
        """
        Driver for a two_wheel_drive object. Sends new speeds to motor server every t = 0.1 seconds. Non-blocking.
        :return:
        """

        def f():
            if (self.started): return
            self.started = True
            with client.ServerProxy(self.host) as proxy:
                while (not self.req_shutdown):
                    self.update_speed(proxy)
                    time.sleep(0.1);
            self.started = False
            self.req_shutdwon = False

        Thread(target=f).start()

    def shutdown(self):
        """
        Set the flag for shutdown request.
        :return:
        """
        self.req_shutdown = True


class motor_interface():
    """
    Motor interface, simple rpc server that takes calls to set the motor speed,
     and get the motor speed(currently not implemented)
    """
    speed = [0, 0]

    def iset_speed(self, s1, s2):
        """
        Sets the motor speed.
        :param s1: left
        :param s2: right
        :return: help message
        """
        self.speed[0] = s1
        self.speed[1] = s2
        motor1(s1 > 0, abs(s1));
        motor2(s2 > 0, abs(s2));
        return "Speed set to <%d,%d>" % (s1, s2)

    def iget_speed(self):
        """
        Get the motor speed (not actually implemented, returns desired speed)
        :return:
        """
        return self.speed


def main():
    """
    Starts up the rpc server for motor interfacing.
    :return: never returns unless killed
    """
    interface = motor_interface()
    server = SimpleXMLRPCServer(("127.0.0.1", rsys.MOTOR_PORT))
    server.register_function(interface.iget_speed, "get_speed")
    server.register_function(interface.iset_speed, "set_speed")
    server.register_function(lambda: True, "is_alive")
    print("Listening on port %d..." % rsys.MOTOR_PORT)
    server.serve_forever()

if __name__ == "__main__":
    main()
