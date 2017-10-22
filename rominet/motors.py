from rominet.pid import PID
import logging
from math import pi


class Motors(object):

    def __init__(self, a_star, odometer):
        self.a_star = a_star
        self.max_cmd = 400.
        self.max_speed = float(1440 * 150 / 60.)  # 1440 ticks per rev, 150 rev per min 60 sec per minute
        self.odometer = odometer
        self.pid_speed_left = PID(0.08, 2, 0, self.max_speed)
        self.pid_speed_right = PID(0.08, 2, 0, self.max_speed)
        self.pid_distance = PID(2, 0.1, 0.0, 1)
        self.pid_yaw = PID(2, 0, 0.0, 1)
        self.set_point_speed_left = 0
        self.set_point_speed_right = 0
        self.set_point_distance = 0
        self.set_point_yaw = 0
        self.last_send_left = -1000
        self.last_send_right = -1000
        self.a_star.motors(0, 0)
        self.odometer.set_odom_measurement_callback(self._odom_measurement_callback)
        self.log = logging.getLogger('romi')

    def convert_command_to_speed(self, x):
        return self.cap(x, 1) * self.max_speed

    def cap(self, x, max):
        if x > max:
            x = max
        if x < -max:
            x = -max
        return x

    def set_speed_target(self, left, right):
        self.odometer.track_odometry()
        self.set_point_speed_left = self.convert_command_to_speed(left)
        self.set_point_speed_right = self.convert_command_to_speed(right)
        self.set_point_distance = 0

    def move_forward(self, distance, speed):
        self.set_point_distance = self.odometer.get_distance() + distance
        self.set_point_yaw = self.odometer.get_yaw()
        self.pid_distance.max_abs_value = self.cap(speed, 1)
        self.odometer.track_odometry()

    def stop(self):
        self.set_point_distance = 0
        self.set_point_speed_left = 0
        self.set_point_speed_right = 0
        self._send_command_to_motors(0, 0)

    def _odom_measurement_callback(self, speed_left, speed_right, x, y, yaw, omega, dist, current_time):

        if self.set_point_distance != 0:
            if abs(dist - self.set_point_distance) < 0.001:
                speed_cmd = 0
                self.set_point_distance = 0
                self.pid_distance.reset()
            else:
                speed_cmd = self.pid_distance.get_output(self.set_point_distance, dist, current_time)

            if self.set_point_yaw - yaw > pi:
                yaw = yaw + 2 * pi
            elif self.set_point_yaw - yaw < -pi:
                yaw = yaw - 2 * pi
            delta = self.pid_yaw.get_output(self.set_point_yaw, yaw, current_time)

            # going backward, right and left motors have an inverted effect on rotation
            if speed_cmd < 0:
                delta = -delta

            self.set_point_speed_left = speed_cmd * self.max_speed * (1 - delta / 2)
            self.set_point_speed_right = speed_cmd * self.max_speed * (1 + delta / 2)
            print("delta:{}".format(speed_cmd, delta))
            print("yaw: {} set_point_yaw:{}\n".format(yaw * 180 / pi, self.set_point_yaw * 180 / pi))

        left_speed_cmd = self.pid_speed_left.get_output(self.set_point_speed_left, speed_left, current_time)
        right_speed_cmd = self.pid_speed_right.get_output(self.set_point_speed_right, speed_right, current_time)

        left_cmd = int(left_speed_cmd * self.max_cmd / self.max_speed)
        right_cmd = int(right_speed_cmd * self.max_cmd / self.max_speed)

        # print("left_cmd: {} right_cmd: {}".format(left_cmd/self.max_cmd, right_cmd/self.max_cmd))
        # print("dist: {} x:{} y:{} \n".format(dist, x, y))
        if self.set_point_speed_left == 0 and self.set_point_speed_right == 0:
            if abs(left_cmd) < 20 and abs(right_cmd) < 20:
                left_cmd = 0
                right_cmd = 0

        self._send_command_to_motors(left_cmd, right_cmd)

    def _send_command_to_motors(self, left, right):
        self.last_send_left = left
        self.last_send_right = right
        self.a_star.motors(left, right)

        if left == 0 and right == 0:
            self.pid_speed_left.reset()
            self.pid_speed_right.reset()
            self.odometer.stop_tracking()
