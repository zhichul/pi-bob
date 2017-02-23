from rcar import rstandardcar
import pygame
import time


def handle(car,keys):
    for key in keys:
        if key == pygame.K_ESCAPE:
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
    period = 50 # ms
    period_s = period/1000

    pygame.init()
    pygame.key.set_repeat(period, period)

    car = rstandardcar.Car()
    car.start()
    keys = set()
    while handle(car,keys):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys.add(event.key)
            if event.type == pygame.KEYUP:
                keys.remove(event.key)
        time.sleep(period_s)
    car.shutdown()
    pygame.quit()
    print("Thank you for using explore. Bye!")

if __name__ == "__main__":
    main("")
