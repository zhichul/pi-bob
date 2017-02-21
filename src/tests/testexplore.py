from rsystem import rmotor
from threading import Thread
from rplugin import explore

def main():
    Thread(target=rmotor.main).start()
    explore.main("")

if __name__ == "__main__":
    main()
