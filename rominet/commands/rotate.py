from math import degrees, pi
from rominet.pid import PID
from rominet.commands.utils import get_yaw_delta
from rominet.commands import Command


class Rotate(Command):

    def __init__(self, yaw, speed):
        super(Rotate, self).__init__()
        self.yaw = yaw
        self.speed = speed
        self.achieved = False
        self.pid_angle = PID(2, 0, 0, 2 * pi * 5)  # max 5 rotation per second
        self.pid_rotation_speed = PID(800, 3000, 0, max_abs_value=speed)
        self.last_speed_cmd = 0

    def get_motor_speeds(self, speed_left, speed_right, x, y, yaw, omega, distance, current_time):
        if abs(degrees(yaw - self.yaw)) < 0.5:
            self.achieved = True
            speed_cmd = 0
        else:
            rotation_speed = get_yaw_delta(self.yaw, yaw, self.pid_angle, current_time)
            speed_cmd = self.pid_rotation_speed.get_output(rotation_speed, omega, current_time)

        return speed_cmd, -speed_cmd
