from rcar import rsimplecar
from rcar import rstandardcar
import os
import sys
import cv2
import copy
from picamera import PiCamera
from training.units import *
import numpy
import time
import datetime
from threading import Thread
from pistreaming import server
import random
import picamera.array
from gopigo import *

RUNNING = True
LSPEED = 150
RSPEED= 130
RADIUS = 2
def userinput():
    global RUNNING
    while True:
        if input("input") == "x":
            break;
    RUNNING = False

def main(arg):
    # initialize input
    # Thread(target=userinput).start()

    #initialize car
    # car = rsimplecar.SimpleCar(speed=180,radius=1.5,freq=10)
    # car = rstandardcar.Car(acceleration=6,radius=3,freq=20)
    # car.start()

    #initialize decision network
    ANN = Network.fromFile(sys.argv[1])
    DNN = Network.fromFile("./training/nnd.save")

    #main loop
    try:
        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as output:
                while RUNNING:
                    output.truncate(0)
                    camera.capture(output, 'rgb',use_video_port=True)
                    img = cv2.cvtColor(output.array, cv2.COLOR_BGR2GRAY)
                    img = cv2.GaussianBlur(img,(5,5),0)
                    img = cv2.resize(img,(16,12))
                    img = np.multiply(1/255,np.ndarray.flatten(img))
                    res = ANN.evaluate(img)

                    L = 0
                    S = 1
                    R = 2
                    DETECT_THRESHOLD = 1
                    COOLING = 2
                    detect_count = 0
                    cooling = 0
                    curr_decision = res.index(max(res))
                    # branch_decisions = [S,S,L,S,S,R,S,S,L,R]
                    # if DNN.evaluate(img)[0] > 0.5:
                    #     print("<BRANCH>")
                    #     if detect_count < DETECT_THRESHOLD:
                    #         detect_count += 1
                    #     else:
                    #         curr_decision = branch_decisions.pop()
                    #         print("<FORCING %d>"%(curr_decision))
                    #         cooling += 1
                    #         if cooling == COOLING:
                    #             detect_count = 0
                    #             cooling = 0
                    # else:
                    #     detect_count = 0
                    #     cooling = 0
                    # motion
                    # if random.random() > 0.2: car.w()
                    if curr_decision == L:
                        left()
                        time.sleep(0.3)
                        # car.a()
                        print("<LEFT>")
                    elif curr_decision == S:
                        straight()
                        print("<STRAIGHT>")
                    elif curr_decision == R:
                        right()
                        # car.d()
                        print("<RIGHT>")
                    else:
                        assert False
                    # input("hit any key to continue")
    except KeyboardInterrupt:
        stop()
    # car.stop()
    # car.shutdown()
    print("Thank you for using auto. Bye!")
def left():
    motor1(1,int(0.6*LSPEED*(1-0.5/RADIUS)))
    motor2(1,int(0.6*RSPEED*(1+0.5/RADIUS)))

def right():
    motor1(1,int(0.8*LSPEED*(1+0.5/RADIUS)))
    motor2(1,int(0.8*RSPEED*(1-0.5/RADIUS)))

def straight():
    motor1(1,LSPEED)
    motor2(1,RSPEED)
def stop():
    motor2(1,0)
    motor1(1,0)
if __name__ == "__main__":
    main("")


#                 if len(sys.argv) > 3: cv2.imwrite(os.path.join(sys.argv[2],str(decision)+"-"+str(datetime.datetime.now())+".jpg"),img0)

