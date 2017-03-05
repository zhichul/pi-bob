from rcar import rsimplecar
import pygame
import time
import os
import sys
from pistreaming import server
from threading import Thread

def handle(car,keys):
    for key in keys:
        if  key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_w:
            car.w()
            # print("Gas")
        elif key == pygame.K_s:
            car.s()
            # print("Brake")
        elif key == pygame.K_a:
            car.a()
            # print("Left")
        elif key == pygame.K_d:
            car.d()
            # print("Right")
        elif key == pygame.K_x:
            car.stop()
            # print("Stop")
        elif key == pygame.K_p:
            print("Need to implement photo capture!")
    return True


def main(arg):
    argv = list(sys.argv)
    argv.pop(0)
    Thread(target=server.main,args=[argv]).start()
    os.environ["SDL_VIDEODRIVER"] = 'dummy'
    period = 50 # ms
    period_s = period/1000

    pygame.init()
    pygame.key.set_repeat(period, period)
    pygame.display.set_mode((1,1))
    car = rsimplecar.SimpleCar(255,2)
    car.start()
    keys = set()
    while handle(car,keys):
        for event in pygame.event.get():
            print("event")
            if event.type == pygame.KEYDOWN:
                keys.add(event.key)
            if event.type == pygame.KEYUP:
                keys.remove(event.key)
        time.sleep(period_s)
    car.shutdown()
    pygame.quit()
    server.running = False
    print("Thank you for using explore. Bye!")

if __name__ == "__main__":
    main("")
