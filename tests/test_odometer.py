import math
import mock
import time
import unittest

from rominet.odometer import Odometer, DISTANCE_PER_TICK_MM, WHEEL_DISTANCE_MM
from rominet.encoders import Encoders


class TestOdometer(unittest.TestCase):

    def test_monitoring_thread_stops(self):
        encoder = mock.MagicMock(spec=Encoders)
        encoder.read_encoders.return_value = 0, 0
        odom = Odometer(encoder)
        odom.track_odometry()

        odom.stop_tracking()
        time.sleep(0.3)

        time.sleep(1)
        encoder.reset_mock()
        encoder.read_encoders.assert_not_called()

    def test_callback(self):
        encoder = mock.MagicMock(spec=Encoders)
        encoder.read_encoders.return_value = 0, 0
        odom = Odometer(encoder)
        callback = mock.MagicMock()
        odom.add_measurement_callback(callback.call_back)
        odom.track_odometry()
        time.sleep(0.1)

        callback.call_back.assert_called()

    def test_distance(self):
        encoder = mock.MagicMock(spec=Encoders)
        encoder.read_encoders.return_value = 0, 0
        odom = Odometer(encoder)
        odom.track_odometry()
        time.sleep(0.1)
        encoder.read_encoders.return_value = 1000, 1000
        time.sleep(0.1)
        distance = odom.get_situation().dist

        self.assertEqual(distance, DISTANCE_PER_TICK_MM)

    def test_yaw(self):
        encoder = mock.MagicMock(spec=Encoders)
        encoder.read_encoders.return_value = 0, 0
        odom = Odometer(encoder)
        odom.track_odometry()
        time.sleep(0.1)

        half_circle = WHEEL_DISTANCE_MM * math.pi / 2
        encoder.read_encoders.return_value = (half_circle / DISTANCE_PER_TICK_MM,
                                              - half_circle / DISTANCE_PER_TICK_MM)
        time.sleep(0.1)
        yaw = odom.get_situation().yaw

        self.assertEqual(math.pi, yaw)

        quarter_circle = half_circle / 2
        encoder.read_encoders.return_value = (quarter_circle / DISTANCE_PER_TICK_MM,
                                              - quarter_circle / DISTANCE_PER_TICK_MM)
        time.sleep(0.1)
        yaw = odom.get_situation().yaw

        self.assertEqual(math.pi / 2, yaw)
