from . import rabstractcar

class Car(rabstractcar.AbstractCar):

    def __init__(self, fric_min=2, fric_max=4, acceleration=16, freq=10):
        """
        Initializes friction and acceleration model
        :param fric_min: upper bound for friction [0,255]
        :param fric_max: lower bound for friction [0,fric_upper]
        :param acceleration: acceleration for emulating gas and brake [0,255]
        """
        super(Car,self).__init__(freq=freq)
        self.acc = acceleration  # gas acceleration
        self.fric_max = fric_max  # friction acceleration upper bound
        self.fric_min = fric_min  # friction acceleration lower bound
        self.speed = 0

    def friction(self,velocity):
        """
        Linear (to velocity) friction calculator.
        f = f0 + kv
        :param velocity: velocity
        :return: the friction
        """
        return int(self.fric_min + velocity / 255 * (self.fric_max - self.fric_min))

    def radius(self, velocity):
        return 1.5 # constant turning radius for now

    def slow_side_velocity(self,velocity,radius):
        return velocity * (1-0.5/radius)

    def fast_side_velocity(self,velocity,radius):
        return velocity * (1+0.5/radius)

    def max_velocity(self,radius):
        """
        Calculates max velocity to make corrections for high speed turning
        :param a: angular velocity
        :return: the max velocity
        """
        return int(255 * radius / (radius + 0.5))

    def new_speed(self):
        x,y,stopped = self.signals()

        if stopped:
            self.speed = 0
            return 0,0

        velocity = self.speed

        # acceleration
        acc = x * self.acc

        # directions of v, acc, and friction
        velocity_dir = velocity / abs(velocity) if velocity != 0 else 0
        acceleration_dir = x
        friction_dir = -1 * velocity_dir if velocity_dir else -1 * acceleration_dir  # if v = 0, use opposite of acc_dir
        assert ((velocity_dir in {-1, 0, 1}) and (acceleration_dir in {-1, 0, 1}) and (friction_dir in {-1, 0, 1}))

        # apply friction and acceleration to velocity
        velocity_new = velocity + acc + friction_dir * self.friction(velocity)
        if velocity * velocity_new < 0: v_new = 0  # crossing 0, force 0

        # turning radius
        radius = self.radius(velocity)

        # if result exceeded max/min cutoff at max/min
        v_max = self.max_velocity(radius) if y else 255
        if velocity_new > v_max:
            velocity_new = v_max
        elif velocity_new < -1 * v_max:
            velocity_new = -1 * v_max

        # applying turning
        if y == 1:
            l = self.slow_side_velocity(velocity_new,radius)
            r = self.fast_side_velocity(velocity_new,radius)
        elif y == -1:
            l = self.fast_side_velocity(velocity_new, radius)
            r = self.slow_side_velocity(velocity_new, radius)
        else:
            l = r = velocity_new
        self.speed = velocity_new
        return l,r

