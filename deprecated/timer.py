import time


# A simple, multi-purpose timer class to manage time steps in loops, control execution times, etc.
class Timer:

    # Constructor starts the timer at instantiation
    def __init__(self):
        self.reset()

    # Method resets the timer initial time to current time
    def reset(self):
        self.initTime = time.time()

    # Method returns the time elapsed since instantiation or last reset minus sum of paused time
    def getElapsed(self):
        return time.time() - self.initTime

    # Method sleeps until elapsed time reaches delay argument then resets the timer
    # Useful to control fixed time step in loops.
    def sleepToElapsed(self, delay):
        if self.getElapsed() < delay:
            time.sleep(delay - self.getElapsed())
        self.reset()
