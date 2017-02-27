"""
Scheduler module for rsys

Thread Count: 3

"""
from threading import Thread
import xmlrpc.client as client
from xmlrpc.server import SimpleXMLRPCServer

import time
from . import rsys
from . import rcam
from . import rmotor

class rscheduler():

    stats = dict()
    stat_fns = dict() # functions to retrieve each stat

    modules = dict()
    module_fns = dict() # functions to start up each module

    def register_stat(self,name,fn):
        self.stats[name] = None
        self.stat_fns[name] = fn

    def register_module(self,name,check_fn,start_fn):
        self.modules[name] = None
        self.module_fns[name] = check_fn,start_fn

    def update_stats(self):
        for item in self.stat_fns.items():
            try:
                self.stats[item[0]] = item[1]()
            except:
                self.stats[item[0]] = None

    def update_modules(self):
        for item in self.module_fns.items():
            try:
                check_fn, start_fn = item[1]
                if check_fn():
                    # mark module as functioning
                    self.modules[item[0]] = True
                else:
                    # try to restart the module
                    self.modules[item[0]] = None
                    Thread(target=start_fn).start()
            except:
                # try to restart the module
                self.modules[item[0]] = None
                Thread(target=start_fn).start()

    def routine_m(self):
        while (True):
            self.update_modules()
            time.sleep(2)

    def routine_s(self):
        while (True):
            self.update_stats()
            time.sleep(2)

    def start(self):
        Thread(target=self.routine_m).start()
        Thread(target=self.routine_s).start()
        server = SimpleXMLRPCServer(("127.0.0.1", rsys.SCHEDULER_PORT),logRequests=False)
        server.register_function(self.get_modules,"get_modules")
        server.register_function(self.get_stats,"get_stats")
        server.register_function(self.register_module,"register_module")
        server.register_function(self.register_stat,"register_stat")
        print("Scheduler up and listening at port %d..." % rsys.SCHEDULER_PORT)
        server.serve_forever()

    def get_stats(self):
        return self.stats

    def get_modules(self):
        return self.modules


############ Monitor job start functions ##########
def check_motor():
    with client.ServerProxy("http://127.0.0.1:%d/" % rsys.MOTOR_PORT) as proxy:
        return proxy.is_alive()

def check_cam():
    with client.ServerProxy("http://127.0.0.1:%d/" % rsys.CAM_PORT) as proxy:
        return proxy.is_alive()

############ Stats job start functions ##########
def speed():
    with client.ServerProxy("http://127.0.0.1:%d/" % rsys.MOTOR_PORT) as proxy:
        return proxy.get_speed()

def main():
    scheduler = rscheduler()
    # register monitor jobs and stat jobs here
    scheduler.register_module("motor", check_motor, rmotor.main)
    scheduler.register_module("cam",check_cam, rcam.main)
    scheduler.register_stat("motor_speed", speed)
    Thread(target=scheduler.start).start()

if __name__ == "__main__":
    main()
