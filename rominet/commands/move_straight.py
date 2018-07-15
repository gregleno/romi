from rominet.pid import PID
from rominet.commands.command import Command
from rominet.commands.utils import get_yaw_delta, cap


class MoveStraight(Command):

    def __init__(self, distance, speed, initial_yaw, initial_distance):
        super(MoveStraight, self).__init__()
        self.distance = distance
        self.initial_distance = initial_distance
        self.initial_yaw = initial_yaw
        self.pid_distance = PID(20, 0, 0.0, speed)
        self.pid_yaw_correction = PID(1, 2, 0.0, 1)

    def get_motor_speeds(self, situation):
        if abs(situation.dist - self.distance) < 0.01 \
            or abs(self.initial_distance - situation.dist) - \
                abs(self.distance) > 0.00:
            self.achieved = True
            speed_cmd = 0
        else:
            speed_cmd = self.pid_distance.get_output(self.distance * 1000, situation.dist * 1000,
                                                     situation.current_time)
        delta = get_yaw_delta(self.initial_yaw, situation.yaw, self.pid_yaw_correction,
                              situation.current_time)

        # going backward, right and left motors have an inverted effect on rotation
        if speed_cmd < 0:
            delta = -delta

        speed_left = cap(speed_cmd * (1 + delta / 2.), 1)
        speed_right = cap(speed_cmd * (1 - delta / 2.), 1)

        return speed_left, speed_right
