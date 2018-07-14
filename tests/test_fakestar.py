import time
import unittest

from rominet.fake_star import FakeAStar
from rominet.motors import Motor


class TestfakeStar(unittest.TestCase):

    def test_encoder(self):
        f = FakeAStar()
        f.motors(Motor.MAX_CMD, Motor.MAX_CMD)
        for i in range(5):
            time.sleep(0.5)
            f.read_encoders()
        f.motors(-Motor.MAX_CMD, -Motor.MAX_CMD)
        for i in range(5):
            time.sleep(0.5)
            f.read_encoders()
        left, right = f.read_encoders()
        self.assertLess(abs(left), 100)
        self.assertLess(abs(right), 100)
