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
SPEED = 150
RADIUS = 2
Kp = 0.2*SPEED
Kd = 0.1*SPEED

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
    error = 0
    lasterror = 0
    #main loop
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            while RUNNING:
                output.truncate(0)
                camera.capture(output, 'rgb',use_video_port=True)
                img = cv2.cvtColor(output.array, cv2.COLOR_BGR2GRAY)
                img = cv2.GaussianBlur(img,(5,5),0)
                img = cv2.resize(img,(16,12))
                img = np.multiply(1,np.ndarray.flatten(img))
                ANN.update(img)
                error = ANN.evaluate(img)[0] - 0.5
                print(error)
                # motion
                lspeed = int(SPEED + Kp * error + Kd * (abs(error)-abs(lasterror)))
                rspeed =int(SPEED - Kp * error - Kd * (abs(error)-abs(lasterror)))
                motor1(1,lspeed)
                motor2(1,rspeed)
                lasterror = error
                time.sleep(0.5)
                motor1(1,0)
                motor2(1,0)
                input("hit any key to continue")
    print("Thank you for using auto. Bye!")
def left():
    motor1(1,int(SPEED*(1-0.5/RADIUS)))
    motor2(1,int(SPEED*(1+0.5/RADIUS)))

def right():
    motor1(1,int(SPEED*(1+0.5/RADIUS)))
    motor2(1,int(SPEED*(1-0.5/RADIUS)))

def straight():
    motor1(1,SPEED)
    motor2(1,SPEED)

if __name__ == "__main__":
    main("")


#                 if len(sys.argv) > 3: cv2.imwrite(os.path.join(sys.argv[2],str(decision)+"-"+str(datetime.datetime.now())+".jpg"),img0)

