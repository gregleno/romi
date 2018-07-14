#!/usr/bin/env python

import os.path
import logging
import time
from rominet.webserver import run_web_server
from rominet.robot import Robot
from rominet.fake_star import FakeAStar


class FakeRobot(Robot):

    def __init__(self):
        super(FakeRobot, self).__init__(a_star=FakeAStar())
        self.frames = [open(os.path.join(os.path.dirname(__file__),
                                         'rominet/images/' + f + '.jpg'), 'rb').read()
                       for f in ['1', '2', '3']]

    def get_camera_frame(self):
        return self.frames[int(time.time()) % 3]


if __name__ == '__main__':
    log = logging.getLogger('romi')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    log.info("fake robot start")
    run_web_server(FakeRobot(), True)
