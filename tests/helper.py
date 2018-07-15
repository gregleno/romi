import time


class TimeProvider(object):
    def __init__(self, increment=0.020):
        self.current_time = time.time()
        self.increment = increment

    def time(self):
        self.current_time += self.increment
        return self.current_time

    def increment_time(self, increment):
        self.current_time += increment
