from rsystem import rmotor
from threading import Thread

def main():
    Thread(target=rmotor.main).start()
