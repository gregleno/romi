#!/usr/bin/env python

import logging
import time
from rominet.webserver import run_web_server


class FakeRobot(object):

    def __init__(self):
        self.position = (0, 0)
        self.start_time = int(round(time.time() * 1000))
        self.frames = [open('images/' + f + '.jpg', 'rb').read() for f in ['1', '2', '3']]

    def set_speed_target(self, left, right):
        log.info("Set speed %f:%f", left, right)

    def stop(self):
        pass

    def read_buttons(self):
        return 0, 1, 0

    def delta_time_ms(self):
        return int(round(time.time() * 1000)) - self.start_time

    def delta_time_s(self):
        return int(round(time.time())) - self.start_time / 1000

    def get_position_xy(self):
        self.position = ((self.delta_time_s() / 7.) % 124, (self.delta_time_s() / 13.) % 223)
        return self.position

    def get_encoders(self):
        return self.delta_time_ms() % 123224, self.delta_time_ms() / 2 % 222283

    def get_yaw(self):
        return (self.delta_time_ms() / 4000.) % 6.28

    def get_camera_frame(self):
        return self.frames[int(time.time()) % 3]

    def get_distance(self):
        return self.delta_time_s()

    def get_speed(self):
        return self.delta_time_ms() % 4000

    def get_max_speed_left_right(self):
        return 3456, 2637

    def set_leds(self, red, yellow, green):
        pass

    def reset_odometry(self):
        self.start_time = int(round(time.time() * 1000))

    def play_notes(self, notes):
        pass

    def get_battery(self):
        return 8000 - (self.delta_time_ms() / 230 % 1000)

    def is_romi_board_connected(self):
        return True


if __name__ == '__main__':
    log = logging.getLogger('romi')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    log.info("fake robot start")
    run_web_server(FakeRobot(), True)
