import time
import unittest

from rominet.fake_star import FakeAStar
from rominet.motors import Motor

from tests.helper import TimeProvider


class TestfakeStar(unittest.TestCase):

    def test_encoder(self):

        time_provider = TimeProvider(0.020)
        f = FakeAStar(time_provider)
        f.motors(Motor.MAX_CMD, Motor.MAX_CMD)
        for i in range(5):
            f.read_encoders()
        f.motors(-Motor.MAX_CMD, -Motor.MAX_CMD)
        for i in range(5):
            f.read_encoders()
        left, right = f.read_encoders()
        self.assertLess(abs(left), 100)
        self.assertLess(abs(right), 100)
