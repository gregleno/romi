import unittest

from rominet.pid import PID


class TestPid(unittest.TestCase):

    def test_max_abs_value(self):
        max_value = 1
        p = PID(Kp=1, Ki=0, Kd=0, max_abs_value=max_value)
        self.assertEqual(p.get_output(3, 1, 0), max_value)
        self.assertEqual(p.get_output(-3, 1, 0), -max_value)

    def test_proportional(self):
        Kp = 0.1
        p = PID(Kp=Kp, Ki=0, Kd=0, max_abs_value=100)
        setup_point = 10
        for i in range(10):
            output = p.get_output(10, i, 0)
            self.assertEqual(output, (setup_point - i) * Kp)

    def test_integration(self):
        p = PID(Kp=0, Ki=0.1, Kd=0, max_abs_value=100)
        setup_point = 10
        measurement = 0
        max_time = 100
        for i in range(max_time):
            measurement = p.get_output(setup_point, measurement, i)
            self.assertLess(measurement, setup_point)

            # We expect to have converged by that time
            if i > 50:
                self.assertLess(setup_point - measurement, 0.1)

    def test_reset(self):
        p = PID(Kp=0, Ki=0.1, Kd=0, max_abs_value=100)
        setup_point = 10
        measurement = 0
        max_time = 100
        for i in range(max_time):
            measurement = p.get_output(setup_point, measurement, i)
        self.assertLess(setup_point - measurement, 0.1)
        p.reset()
        measurement = p.get_output(setup_point, measurement, max_time+1)
        self.assertEqual(measurement, 0)
