import unittest

from rominet.motor import Motor


class TestMotor(unittest.TestCase):

    def test_get_speed_command(self):
        m = Motor()
        model = MotorModel()
        m.set_speed(1)
        measured_speed = 0
        for i in range(1, 100):
            cmd = m.get_speed_command(measured_speed, i)
            measured_speed = model.get_new_speed(cmd)
            # print("{} {}".format(cmd, measured_speed))
            self.assertGreater(cmd, 0)

    def test_max_speed(self):
        m = Motor()
        with self.assertRaises(ValueError):
            m.set_speed(2)
        with self.assertRaises(ValueError):
            m.set_speed(-2)

    def test_convert_command_to_speed(self):
        self.assertEqual(Motor.convert_command_to_speed(0.5), Motor.MAX_SPEED / 2)
        self.assertEqual(Motor.convert_command_to_speed(-0.5), -Motor.MAX_SPEED / 2)
        self.assertEqual(Motor.convert_command_to_speed(2), Motor.MAX_SPEED)
        self.assertEqual(Motor.convert_command_to_speed(-2), -Motor.MAX_SPEED)


class MotorModel(object):
    def __init__(self):
        self.last_cmd = 0

    def get_new_speed(self, cmd):
        prev_speed = self.last_cmd * Motor.MAX_SPEED / Motor.MAX_CMD
        new_speed = cmd * Motor.MAX_SPEED / Motor.MAX_CMD
        self.last_cmd = cmd

        return (prev_speed + new_speed) / 2

