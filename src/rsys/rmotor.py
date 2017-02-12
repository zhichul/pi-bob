# Mid-level interface for manipulating motors
from xmlrpc.server import SimpleXMLRPCServer
from . import rsys

def main():
    server = SimpleXMLRPCServer(("localhost", rsys.MOTOR_PORT))
    print("Listening on port %d..." % rsys.MOTOR_PORT)
    server.register_function(lambda:True, "is_alive")
    server.serve_forever()