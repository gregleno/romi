from math import degrees, pi
from rominet.pid import PID
from rominet.commands.utils import get_yaw_delta
from rominet.commands.command import Command


class Rotate(Command):

    def __init__(self, yaw, speed):
        super(Rotate, self).__init__()
        self.yaw = yaw
        self.speed = speed
        self.pid_angle = PID(2, 0, 0, 2 * pi * 5)  # max 5 rotation per second
        self.pid_rotation_speed = PID(800, 3000, 0, max_abs_value=speed)
        self.last_speed_cmd = 0

    def get_motor_speeds(self, situation):
        if abs(degrees(situation.yaw - self.yaw)) < 0.5:
            self.achieved = True
            speed_cmd = 0
        else:
            rotation_speed = get_yaw_delta(self.yaw, situation.yaw, self.pid_angle,
                                           situation.current_time)
            speed_cmd = self.pid_rotation_speed.get_output(rotation_speed, situation.omega,
                                                           situation.current_time)

        return speed_cmd, -speed_cmd
