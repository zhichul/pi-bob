class Service(object):
    """
      A abstract superclass for a service.
    """

    running = False
    registry = None

    def name(self):
        """
        To be overriden by subclass
        :return: the name of service
        """
        return "Unimplemented"

    def update(self, data):
        if self.registry:
            self.registry.broadcast(self.name(), data)

    def do_work(self):
        """
        while self.running:
            wait for update
            do something
        """

    def start(self):
        self.running = True
        self.do_work()

    def stop(self):
        self.running = False
