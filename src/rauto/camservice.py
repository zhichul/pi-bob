import time
import io
from queue import Queue
from picamera import PiCamera
from threading import Thread
from threading import Lock

from .service import Service


class CamService(Service):

    def __init__(self,fps=30,burst_size=5):
        self.fps = fps
        self.period = 1/fps
        self.lock = Lock()
        self.capturing = False
        self.camera = PiCamera()
        self.burst_size = burst_size
        self.buffer_pool = Queue()
        self.capture = False

    def timer(self):
        while self.running:
            time.sleep(self.period)
            self.capture = True

    def do_work(self):
        Thread(target=self.timer).start()
        while self.running:
            if not self.capture or not self.registry:
                continue
            self.capture = False

            # loop through the pool and try to find a spare buffer
            found_empty = False
            for i in range(self.buffer_pool.qsize()):
                buffer = self.buffer_pool.get()
                self.buffer_pool.put(buffer)
                if buffer.lock.acquire(blocking=False):  # found spare buffer
                    self.camera.capture_sequence(buffer.get_buffer(), use_video_port=True)
                    buffer.lock.release()
                    Thread(self.registry.broadcast(self.name(),buffer)).start()
                    found_empty = True
                    break

            # if every buffer is currently in use, create a new buffer
            if not found_empty:
                new_buffer = BurstBuffer(self.burst_size)
                self.buffer_pool.put(new_buffer)
                self.camera.capture_sequence(new_buffer.get_buffer(), use_video_port=True)
                Thread(self.registry.broadcast(self.name(), new_buffer)).start()
                continue

    def buffer_count(self):
        return self.buffer_pool.qsize()

class BurstBuffer(object):

    def __init__(self,n):
        self.buffer = [io.BytesIO() for i in range(n)]
        self.lock = Lock()

    def get_buffer(self):
        return self.buffer