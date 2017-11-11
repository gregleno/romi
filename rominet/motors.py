from pid import PID
import logging
from math import pi
from commands.speed import Speed
from commands.move_straight import MoveStraight
from commands.rotate import Rotate


class Motors(object):

    max_speed = float(1440 * 150 / 60.)
    max_acceleration = max_speed / 10  # Max speed achieved in 10 iterations

    def __init__(self, a_star, odometer):
        self.a_star = a_star
        self.max_cmd = 400.

        # 1440 ticks per rev, 150 rev per min 60 sec per minute
        self.odometer = odometer
        self.pid_speed_left = PID(0.1, 5, 0, Motors.max_speed)
        self.pid_speed_right = PID(0.1, 5, 0, Motors.max_speed)
        self.last_speed_cmd_left = 0
        self.last_speed_cmd_right = 0
        self.command = None
        self.last_send_left = -1000
        self.last_send_right = -1000
        self.a_star.motors(0, 0)
        self.odometer.set_odom_measurement_callback(self._odom_measurement_callback)
        self.log = logging.getLogger('romi')

    @staticmethod
    def convert_command_to_speed(x):
        if x > 1:
            x = 1
        if x < -1:
            x = -1
        return x * Motors.max_speed

    def set_speed_target(self, left, right):
        if self.command is None or type(self.command) != Speed:
            self.command = Speed(self.convert_command_to_speed(left),
                                 self.convert_command_to_speed(right))
        else:
            self.command.set_target_speed(self.convert_command_to_speed(left),
                                          self.convert_command_to_speed(right))

        if left == 0 and right == 0:
            self.reset_pids()
            self.odometer.stop_tracking()
        else:
            self.odometer.track_odometry()

    def move_forward(self, distance, speed):
        self.command = MoveStraight(self.odometer.get_distance() + distance,
                                    self.convert_command_to_speed(speed),
                                    self.odometer.get_yaw(), self.odometer.get_distance())
        self.reset_pids()
        self.odometer.track_odometry()

    def rotate(self, angle, speed):
        self.command = Rotate((self.odometer.get_yaw() + angle) % (2 * pi),
                              self.convert_command_to_speed(speed))
        self.reset_pids()
        self.odometer.track_odometry()

    def stop(self):
        self._send_command_to_motors(0, 0)
        self.odometer.stop_tracking()
        self.reset_pids()

    def _odom_measurement_callback(self, speed_left, speed_right, x, y, yaw, omega, dist,
                                   current_time):
        command = self.command
        if command is not None and not command.is_achieved():
            set_point_speed_left, \
                set_point_speed_right = command.get_motor_speeds(speed_left, speed_right,
                                                                 x, y, yaw, omega,
                                                                 dist, current_time)
            if command.is_achieved():
                self.odometer.stop_tracking()
        else:
            set_point_speed_left = 0
            set_point_speed_right = 0

        left_speed_cmd = self.pid_speed_left.get_output(set_point_speed_left, speed_left,
                                                        current_time)
        right_speed_cmd = self.pid_speed_right.get_output(set_point_speed_right, speed_right,
                                                          current_time)

        # Make sure that we do not accelerate or decelerate too fast
        left_speed_cmd = self.cap_acceleration(left_speed_cmd, self.last_speed_cmd_left)
        right_speed_cmd = self.cap_acceleration(right_speed_cmd, self.last_speed_cmd_right)

        self.last_speed_cmd_left = left_speed_cmd
        self.last_speed_cmd_right = right_speed_cmd

        # Convert to a command that can be sent to A*
        left_cmd = int(left_speed_cmd * self.max_cmd / self.max_speed)
        right_cmd = int(right_speed_cmd * self.max_cmd / self.max_speed)

        if set_point_speed_left == 0 and set_point_speed_right == 0:
            if abs(left_cmd) < 30 and abs(right_cmd) < 30:
                left_cmd = 0
                right_cmd = 0

        self._send_command_to_motors(left_cmd, right_cmd)

    def _send_command_to_motors(self, left, right):
        self.last_send_left = left
        self.last_send_right = right
        self.a_star.motors(left, right)

    def reset_pids(self):
        self.pid_speed_left.reset()
        self.pid_speed_right.reset()

    @staticmethod
    def cap_acceleration(speed_cmd, last_speed_cmd):
        """Ensure that we do not accelerate more than Motors.max_acceleration at each iteration."""

        if (speed_cmd - last_speed_cmd) > Motors.max_acceleration:
            speed_cmd = last_speed_cmd + Motors.max_acceleration
        elif (last_speed_cmd - speed_cmd) > Motors.max_acceleration:
            speed_cmd = last_speed_cmd - Motors.max_acceleration
        return speed_cmd
