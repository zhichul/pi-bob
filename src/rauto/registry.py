from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
from rsystem import rsys


class Registry(object):
    """
    Register services and service listeners under a registry object and push/receive updates.
    """
    def __init__(self):
        self.services = dict() # dictionary of (String name, Service serviceobject) pairs
        self.subscriptions = dict() # dictionary of (String id, Set<Subscriber> subscribers) pairs

    def register_service(self,name,service):
        self.services[name] = service
        service.registry = self

    def register_subscriber(self,name,subscriber):
        """
        Make a subscription to the service <name>.
        :param name: a service name (does not have to be a pre-existing one)
        :param subscriber: the object that wants to listen to the updates of <name>
        :return: None
        """
        if name not in self.services:
            # the case where a subscription happened before a service was registered
            # the subscriber will not be notified of updates until there is actually a service object under <name>
            print("<Warning> Service %s has not been registered. However, subscribing anyway.")
        if name not in self.subscriptions:
            self.subscriptions[name] = set()
        self.subscriptions[name].add(subscriber)
        subscriber.registry = self

    def broadcast(self,name,data):
        """
        Broadcast an update of a service to all subscribers
        :param name: name of service
        :param data: the data update
        :return: None
        """
        for subscriber in self.subscriptions[name]:
            Thread(target=subscriber.update,args=(name,data)).start()

    def start_remote(self):
        """
        Run in remote mode. Might not be most efficient.
        :return:
        """
        server = SimpleXMLRPCServer(("127.0.0.1", rsys.REGISTRY_PORT), logRequests=False)
        server.register_function(self.register_service, "register_service")
        server.register_function(self.register_subscriber, "register_subscriber")
        server.register_function(self.broadcast, "broadcast")
        server.register_function(lambda: True, "is_alive")
        print("Registry running on port %d..." % rsys.REGISTRY_PORT)
        server.serve_forever()


