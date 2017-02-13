# Mid-level interface for manipulating camera
# Thread Count: 1
from xmlrpc.server import SimpleXMLRPCServer
from rsystem import rsys

def main():
    server = SimpleXMLRPCServer(("localhost", rsys.CAM_PORT))
    print("Listening on port %d..." % rsys.CAM_PORT)
    server.register_function(lambda:True, "is_alive")
    server.serve_forever()