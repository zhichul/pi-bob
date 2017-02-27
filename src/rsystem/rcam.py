# Mid-level interface for manipulating camera
# Thread Count: 1
from xmlrpc.server import SimpleXMLRPCServer
from . import rsys

def main():
    server = SimpleXMLRPCServer(("127.0.0.1", rsys.CAM_PORT),logRequests=False)
    print("Listening on port %d..." % rsys.CAM_PORT)
    server.register_function(lambda:True, "is_alive")
    server.serve_forever()