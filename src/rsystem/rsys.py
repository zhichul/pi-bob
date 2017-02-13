# system thread
from threading import Thread

SCHEDULER_PORT = 8000
MOTOR_PORT = 8001
CAM_PORT = 8002

from . import rscheduler

def server(port):
    return "localhost:%d" % port

class Rsys():
    """
    System object
    """

    def start(self):
        """
        Starts up the system threads as daemon
        :return:
        """
        Thread(target=rscheduler.main).start()
        pass


def main():
    Rsys().start()