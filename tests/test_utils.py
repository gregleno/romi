import math
import unittest

from rominet.commands.utils import get_yaw_delta
from rominet.pid import PID


class TestMotors(unittest.TestCase):

    def test_get_yaw_delta(self):
        for i in range(-10, 10, 1):
            delta = get_yaw_delta(0, i, PID(1), 1)
            self.assertLess(delta, math.pi)
            self.assertGreater(delta, -math.pi)
