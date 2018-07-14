from math import pi
from commands import Speed
from commands import MoveStraight
from commands import Rotate
from rominet.motor import Motor


class Motors(object):

    def __init__(self, a_star, odometer):
        self.a_star = a_star

        self.odometer = odometer
        self.command = None
        self.left_motor = Motor()
        self.right_motor = Motor()
        self.a_star.motors(0, 0)
        self.odometer.add_measurement_callback(self._odom_measurement_callback)

    def set_speed_target(self, left, right):
        if not self.command or not isinstance(self.command, Speed):
            self.command = Speed(left, right)
        else:
            self.command.set_target_speed(left, right)

        if left == 0 and right == 0:
            self.odometer.stop_tracking()
        else:
            self.odometer.track_odometry()

    def move_forward(self, distance, speed):
        self.command = MoveStraight(self.odometer.get_situation().dist + distance, speed,
                                    self.odometer.get_situation().yaw,
                                    self.odometer.get_situation().dist)
        self.odometer.track_odometry()

    def rotate(self, angle, speed):
        self.command = Rotate((self.odometer.get_situation().yaw + angle) % (2 * pi), speed)
        self.odometer.track_odometry()

    def stop(self):
        self.set_speed_target(0, 0)

    def _odom_measurement_callback(self, situation):
        if self.command and not self.command.is_achieved():
            speed_left, speed_right = self.command.get_motor_speeds(situation)
            if self.command.is_achieved():
                self.odometer.stop_tracking()
        else:
            speed_left, speed_right = 0, 0
        self.left_motor.set_speed(speed_left)
        self.right_motor.set_speed(speed_right)

        left_cmd = self.left_motor.get_speed_command(situation.speed_l, situation.current_time)
        right_cmd = self.right_motor.get_speed_command(situation.speed_r, situation.current_time)

        self._send_command_to_motors(left_cmd, right_cmd)

    def _send_command_to_motors(self, left, right):
        self.a_star.motors(left, right)
