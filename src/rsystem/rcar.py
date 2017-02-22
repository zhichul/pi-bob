from threading import Thread

import time
import xmlrpc.client as client
from . import rsys

class abstract_car():
    host = rsys.server(rsys.MOTOR_PORT)  # address of server hosting motor communication interface
    req_shutdown = False  # flag for shutting down the thread running from start()
    started = False  # flag for indicating there is already a thread running from start()
    com_freq = 0.1 # communication frequency x times per second

    def update_speed(self,proxy):
        # to be overriden by subclass
        pass

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
                    time.sleep(self.com_freq);
            self.started = False
            self.req_shutdwon = False

        Thread(target=f).start()

    def shutdown(self):
        """
        Set the flag for shutdown request.
        :return:
        """
        self.req_shutdown = True

