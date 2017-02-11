# system thread
from threading import Thread
import threading

from . import rsh

class Rsys():
    """
    System object
    """

    def start(self):
        """
        Starts up the system threads as daemon
        :return:
        """
        Thread(target=rsh.main).start()
        pass


def main():
    Rsys().start()