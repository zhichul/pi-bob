from threading import Thread, Lock

import time
import xmlrpc.client as client
from rsystem import rsys
from gopigo import *

class AbstractCar():
    host = rsys.server(rsys.MOTOR_PORT)  # address of server hosting motor communication interface
    req_shutdown = False  # flag for shutting down the thread running from start()
    started = False  # flag for indicating there is already a thread running from start()
    stopped = False # Car stopped
    x = 0 # fwd bckwd direction signal {-1, 0, 1}
    y = 0 # left right signal {-1, 0, 1} 1 for left

    def __init__(self,freq=10):
        self.com_freq = 1/freq # communication frequency in terms of freq times per second

    def w(self):  # fwd
        self.x = 1

    def a(self):  # left
        self.y = 1

    def s(self):  # bkwd
        self.x = -1

    def d(self):  # right
        self.y = -1

    def stop(self):
        self.stopped = True

    def signals(self): # get and clear signals
        res = (self.x,self.y,self.stopped)
        self.x,self.y,self.stopped= (0,0,False)
        return res

    def new_speed(self):
        pass

    def update_speed(self,proxy):
        l,r = self.new_speed()
        #proxy.set_speed(l,r)
        motor1(l > 0, abs(l))
        motor2(r > 0, abs(r))

    def start(self):
        """
        Driver for a car object. Sends new speeds to motor server every t = com_freq seconds. Non-blocking.
        :return:
        """
        def f():
            if (self.started): return
            self.started = True
            with client.ServerProxy(self.host) as proxy:
                while (not self.req_shutdown):
                    self.update_speed(proxy)
                    time.sleep(self.com_freq)
            self.started = False
            self.req_shutdwon = False

        Thread(target=f).start()

    def shutdown(self):
        """
        Set the flag for shutdown request.
        :return:
        """
        self.req_shutdown = True

