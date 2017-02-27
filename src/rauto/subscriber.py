class Subscriber(object):
    """
    An abstract superclass for a subscriber
    """
    running = False
    registry = None

    def update(self, name, data):
        """
        To be overriden by subclasses
        :param name: the name of the service which pushed this update
        :param data: the update info
        :return: None
        """
        pass

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
