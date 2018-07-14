import mock
import time
import unittest

from rominet.a_star import AStar
from rominet.fake_star import FakeAStar
from rominet.motors import Motors
from rominet.motor import Motor
from rominet.odometer import Odometer
from rominet.encoders import Encoders


class TestMotors(unittest.TestCase):

    def test_motors(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        m = Motors(a_star, Odometer(Encoders(a_star)))
        m.set_speed_target(1, 1)
        m.set_speed_target(1, 1)
        time.sleep(0.5)

        a_star.read_encoders.assert_called()

    def test_move_forward(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        m = Motors(a_star, Odometer(Encoders(a_star)))
        m.move_forward(1, 1)
        time.sleep(0.5)

        a_star.read_encoders.assert_called()
        a_star.motors.assert_called()

    def test_rotate(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        m = Motors(a_star, Odometer(Encoders(a_star)))
        m.rotate(3.14, 1)
        time.sleep(0.5)

        a_star.read_encoders.assert_called()
        self.assertTrue([c for c in a_star.motors.call_args_list if c != mock.call(0, 0)])

    def test_rotate_done(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        m = Motors(a_star, Odometer(Encoders(a_star)))
        m.rotate(0, 1)
        time.sleep(0.5)

        # Motors should not move
        self.assertFalse([c for c in a_star.motors.call_args_list if c != mock.call(0, 0)])


class TestModel(unittest.TestCase):

    def test_acceleration(self):
        fake_star = FakeAStar()
        m = Motors(fake_star, Odometer(Encoders(fake_star)))
        m.set_speed_target(1, 1)
        time.sleep(0.5)
        left, right = fake_star.cmd
        self.assertLess(abs(Motor.MAX_CMD - left), 10)
        self.assertLess(abs(Motor.MAX_CMD - right), 10)

    def test_stop(self):
        fake_star = FakeAStar()
        m = Motors(fake_star, Odometer(Encoders(fake_star)))
        m.set_speed_target(1, 1)
        time.sleep(0.1)
        m.stop()
        time.sleep(0.3)
        left, right = fake_star.cmd
        self.assertLess(abs(left), 10)
        self.assertLess(abs(right), 10)

    def test_rotate(self):
        fake_star = FakeAStar()
        odom = Odometer(Encoders(fake_star))
        m = Motors(fake_star, odom)
        m.rotate(3.14, 1)
        time.sleep(2)
        self.assertLess(abs(3.14 - odom.get_situation().yaw), 0.1)
        self.assertLess(abs(odom.get_situation().dist), 0.1)

    def test_forward(self):
        fake_star = FakeAStar()
        odom = Odometer(Encoders(fake_star))
        m = Motors(fake_star, odom)
        m.move_forward(1, 1)
        time.sleep(2)
        self.assertLess(abs(1 - odom.get_situation().dist), 0.1)
        self.assertLess(abs(odom.get_situation().yaw), 0.1)
