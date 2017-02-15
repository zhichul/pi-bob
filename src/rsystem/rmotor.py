# Mid-level interface for manipulating motors
# Thread count: 2

from xmlrpc.server import SimpleXMLRPCServer

from . import rsys

class motor_interface():

    speed_desired = [0,0]
    speed_actual = [0,0]

    def set_speed(self, s1, s2):
        self.speed_desired[0] = s1
        self.speed_desired[1] = s2
        # write to the motor
        return "Desired speed set to <%d,%d>" % (s1, s2)

    def get_speed_desired(self):
        return self.speed_desired

    def get_speed_actual(self):
        s1, s2 = self.read()
        self.speed_actual[0] = s1
        self.speed_actual[1] = s2
        return self.speed_actual

    def read(self):
        return (42,42)

def main():
    interface = motor_interface()
    server = SimpleXMLRPCServer(("127.0.0.1", rsys.MOTOR_PORT))
    server.register_function(interface.get_speed_actual,"get_speed_actual")
    server.register_function(interface.get_speed_desired,"get_speed_desired")
    server.register_function(interface.set_speed,"set_speed")
    server.register_function(lambda:True, "is_alive")
    print("Listening on port %d..." % rsys.MOTOR_PORT)
    server.serve_forever()