# Mid-level interface for manipulating motors
# Thread count: 2

from gopigo import *
import atexit

atexit.register(stop)

from . import rsys
from xmlrpc.server import SimpleXMLRPCServer

class motor_interface():
    """
    Motor interface, simple rpc server that takes calls to set the motor speed,
     and get the motor speed(currently not implemented)
    """
    speed = [0, 0]

    def iset_speed(self, s1, s2):
        """
        Sets the motor speed.
        :param s1: left
        :param s2: right
        :return: help message
        """
        self.speed[0] = s1
        self.speed[1] = s2
        motor1(s1 > 0, abs(s1));
        motor2(s2 > 0, abs(s2));
        return "Speed set to <%d,%d>" % (s1, s2)

    def iget_speed(self):
        """
        Get the motor speed (not actually implemented, returns desired speed)
        :return:
        """
        return self.speed


def main():
    """
    Starts up the rpc server for motor interfacing.
    :return: never returns unless killed
    """
    interface = motor_interface()
    server = SimpleXMLRPCServer(("127.0.0.1", rsys.MOTOR_PORT),logRequests=False)
    server.register_function(interface.iget_speed, "get_speed")
    server.register_function(interface.iset_speed, "set_speed")
    server.register_function(lambda: True, "is_alive")
    print("Listening on port %d..." % rsys.MOTOR_PORT)
    server.serve_forever()

if __name__ == "__main__":
    main()
