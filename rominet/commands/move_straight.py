from rominet.pid import PID
from rominet.commands.command import Command
from rominet.commands.utils import get_yaw_delta


class MoveStraight(Command):

    def __init__(self, distance, speed, initial_yaw, initial_distance):
        super(MoveStraight, self).__init__()
        self.distance = distance
        self.initial_distance = initial_distance
        self.speed = speed
        self.initial_yaw = initial_yaw
        self.achieved = False
        self.pid_distance = PID(20, 0, 0.0, speed)
        self.pid_yaw_correction = PID(1, 2, 0.0, 1)
        self.last_speed_cmd = 0

    def get_motor_speeds(self, speed_left, speed_right, x, y, yaw, omega, distance, current_time):
        if abs(distance - self.distance) < 0.01 \
            or abs(self.initial_distance - distance) - \
                abs(self.distance) > 0.00:
            self.achieved = True
            speed_cmd = 0
        else:
            speed_cmd = self.pid_distance.get_output(self.distance * 1000, distance * 1000,
                                                     current_time)
        delta = get_yaw_delta(self.initial_yaw, yaw,  self.pid_yaw_correction, current_time)

        # going backward, right and left motors have an inverted effect on rotation
        if speed_cmd < 0:
            delta = -delta

        set_point_speed_left = speed_cmd * (1 + delta / 2.)
        set_point_speed_right = speed_cmd * (1 - delta / 2.)

        return set_point_speed_left, set_point_speed_right
