from rsystem import rmotor
from threading import Thread
from rplugin import explore
import os

def main():
    t = Thread(target=rmotor.main)
    t.start()
    explore.main("")
    os._exit(0)

if __name__ == "__main__":
    main()
