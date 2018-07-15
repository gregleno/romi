import math
import mock
import time
import unittest

from rominet.a_star import AStar
from rominet.fake_star import FakeAStar
from rominet.motors import Motors
from rominet.motor import Motor
from rominet.odometer import Odometer
from rominet.encoders import Encoders

from tests.helper import TimeProvider


class TestMotors(unittest.TestCase):

    def test_motors(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        odom = Odometer(Encoders(a_star), start_tracking_thread=False)
        m = Motors(a_star, odom)

        m.set_speed_target(1, 1)
        m.set_speed_target(1, 1)
        odom.update(time.time())
        a_star.read_encoders.assert_called()

    def test_move_forward(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        odom = Odometer(Encoders(a_star), start_tracking_thread=False)
        m = Motors(a_star, odom)
        m.move_forward(1, 1)
        odom.update(time.time())

        a_star.read_encoders.assert_called()
        a_star.motors.assert_called()

    def test_rotate(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        odom = Odometer(Encoders(a_star), start_tracking_thread=False)
        m = Motors(a_star, odom)
        m.rotate(3.14, 1)
        odom.update(time.time())

        a_star.read_encoders.assert_called()
        self.assertTrue([c for c in a_star.motors.call_args_list if c != mock.call(0, 0)])

    def test_rotate_done(self):
        a_star = mock.MagicMock(spec=AStar)
        a_star.read_encoders.return_value = 0, 0
        odom = Odometer(Encoders(a_star), start_tracking_thread=False)
        m = Motors(a_star, odom)
        m.rotate(0, 1)
        odom.update(time.time())

        # Motors should not move
        self.assertFalse([c for c in a_star.motors.call_args_list if c != mock.call(0, 0)])


class TestModel(unittest.TestCase):

    def test_acceleration(self):
        time_provider = TimeProvider(increment=0)
        fake_star = FakeAStar(time_provider)
        odom = Odometer(Encoders(fake_star), start_tracking_thread=False)
        m = Motors(fake_star, odom)

        m.set_speed_target(1, 1)

        self.update_odometry(0.5, 0.020, odom, time_provider)

        left, right = fake_star.cmd
        self.assertLess(abs(Motor.MAX_CMD - left), 10)
        self.assertLess(abs(Motor.MAX_CMD - right), 10)

    def test_stop(self):
        time_provider = TimeProvider(increment=0)
        fake_star = FakeAStar(time_provider)
        odom = Odometer(Encoders(fake_star), start_tracking_thread=False)
        m = Motors(fake_star, odom)

        m.set_speed_target(1, 1)

        self.update_odometry(0.5, 0.020, odom, time_provider)

        m.stop()

        self.update_odometry(0.5, 0.020, odom, time_provider)

        left, right = fake_star.cmd
        self.assertLess(abs(left), 10)
        self.assertLess(abs(right), 10)

    def test_rotate(self):
        time_provider = TimeProvider(increment=0)
        fake_star = FakeAStar(time_provider)
        odom = Odometer(Encoders(fake_star), start_tracking_thread=False)
        m = Motors(fake_star, odom)

        m.rotate(math.pi, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        self.assertLess(abs(math.pi - odom.get_situation().yaw), 0.1)
        self.assertLess(abs(odom.get_situation().dist), 0.1)

    def test_forward(self):
        time_provider = TimeProvider(increment=0)
        fake_star = FakeAStar(time_provider)
        odom = Odometer(Encoders(fake_star), start_tracking_thread=False)
        m = Motors(fake_star, odom)

        m.move_forward(1, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        situation = odom.get_situation()
        self.assertLess(abs(1 - situation.dist), 0.1)
        self.assertLess(abs(self.get_delta(situation.yaw, 0)), 0.1)

    def test_square(self):
        time_provider = TimeProvider(increment=0)
        fake_star = FakeAStar(time_provider)
        odom = Odometer(Encoders(fake_star), start_tracking_thread=False)
        m = Motors(fake_star, odom)

        m.move_forward(1, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        self.assertLess(abs(odom.get_situation().dist - 1), 0.1)

        m.rotate(math.pi/2, 1)
        self.update_odometry(4, 0.020, odom, time_provider)
        self.assertLess(abs(self.get_delta(odom.get_situation().yaw, math.pi/2)), 0.1)
        self.assertLess(abs(self.get_delta(odom.get_situation().yaw, math.pi/2)), 0.5)

        m.move_forward(1, 1)
        self.update_odometry(3, 0.020, odom, time_provider)

        self.assertLess(abs(odom.get_situation().dist - 2), 0.15)

        m.rotate(math.pi/2, 1)
        self.update_odometry(3, 0.020, odom, time_provider)

        self.assertLess(abs(self.get_delta(odom.get_situation().yaw, math.pi)), 0.1)

        m.move_forward(1, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        self.assertLess(abs(odom.get_situation().dist - 3), 0.15)

        m.rotate(math.pi/2, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        self.assertLess(abs(self.get_delta(odom.get_situation().yaw, 3 * math.pi/2)), 0.3)

        m.move_forward(1, 1)
        self.update_odometry(2, 0.020, odom, time_provider)

        self.assertLess(abs(odom.get_situation().dist - 4), 0.2)

        m.rotate(math.pi/2, 1)
        self.update_odometry(3, 0.020, odom, time_provider)

        distance_from_zero = math.sqrt(odom.get_situation().x ** 2 + odom.get_situation().y ** 2)
        self.assertLess(distance_from_zero, 0.2)
        self.assertLess(abs(self.get_delta(odom.get_situation().yaw, 0)), 0.1)

    @staticmethod
    def get_delta(angle, reference):
        angle = angle % (2 * math.pi)
        reference = reference % (2 * math.pi)

        if angle - reference > math.pi:
            return (angle - reference) - 2 * math.pi
        elif angle - reference < -math.pi:
            return (angle - reference) + 2 * math.pi
        return angle - reference

    @staticmethod
    def update_odometry(duration_seconds, time_increment, odom, time_provider):
        iterations = int(duration_seconds / time_increment)
        for i in range(iterations):
            time_provider.increment_time(time_increment)
            odom.update(time_provider.time())
