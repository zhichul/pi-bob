from . import rabstractcar


class SimpleCar(rabstractcar.AbstractCar):
    """
    Simple car able of moving forward, backward and turning at constant speed (radius)
    """

    def __init__(self,speed=200,radius=2,freq=10):
        """
        Specifies speed and turning radius of the car.
        :param speed:
        :param radius: radius of turning given as a multiple of car width
        Diagram of top view

                           ^
                          |
                         | direction that the car is moving in
                         |
        |      | -------|      |-------|      |
        |      | -------|      |-------|      |
        |lwheel| -------|middle|-------|rwheel| --------------------------------|center of turning|
        |      | -------|      |-------|      |
        |      | -------|      |-------|      |

        <--------------- width --------------->
                         <------------------------------- radius * width ------------------------->
        """
        assert (speed > 0,radius >= 0.5)
        super.__init__(self,freq)
        self.regular_speed = min(int(speed),255)
        self.slow_speed = int(speed - 0.5 * speed / radius)
        self.fast_speed = int(speed + 0.5 * speed / radius)

    def new_speed(self):
        x,y = self.signals()
        if x == 0:
            return (0,0)
        elif y == 0:
            return x * self.regular_speed, x * self.regular_speed
        elif y == -1:
            return ((x * self.fast_speed, x * self.slow_speed) if x > 0
                    else (x * self.slow_speed, x * self.fast_speed))
        elif y == 1:
            return ((x * self.slow_speed, x * self.fast_speed) if x > 0
                    else (x * self.fast_speed, x * self.slow_speed))
        else:
            assert False

