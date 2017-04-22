import logging


class Motors:

    def __init__(self, a_star):
        self.a_star = a_star
        self.trim_left = 1
        self.trim_right = 1
        self.maxCmd = 300

    def move(self, left, right):
        self.a_star.motors(left * self.trim_left * self.maxCmd,
                           right * self.trim_right * self.maxCmd)

    def stop(self):
        self.aStar.motors(0, 0)
