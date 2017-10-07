from rominet.pid import PID


class Motors(object):

    def __init__(self, a_star, odometer):
        self.a_star = a_star
        self.max_cmd = 400
        self.max_speed = 150 * 1440 / 60
        self.odometer = odometer
        self.pid_left = PID(0.1, 3, 0, self.max_speed)
        self.pid_right = PID(0.1, 3, 0, self.max_speed)
        self.set_point_left = 0
        self.set_point_right = 0
        self.last_send_left = -1000
        self.last_send_right = -1000
        self.odometer.set_odom_measurement_callback(self._odom_measurement_callback)

    def set_speed_target(self, left, right):
        if left != 0 and right != 0:
            self.odometer.track_odometry()
        self.set_point_left = left * self.max_speed
        self.set_point_right = right * self.max_speed

    def stop(self):
        self._send_command_to_motors(0, 0)

    def _odom_measurement_callback(self, speed_left, speed_right, x, y, yaw, omega, current_time):
        left_speed_cmd = self.pid_left.get_output(self.set_point_left, speed_left, current_time)
        right_speed_cmd = self.pid_right.get_output(self.set_point_right, speed_right, current_time)

        left_cmd = int(left_speed_cmd * self.max_cmd / self.max_speed)
        right_cmd = int(right_speed_cmd * self.max_cmd / self.max_speed)
        if self.set_point_left == 0 and self.set_point_right == 0:
            if abs(left_cmd) < 20 and abs(right_cmd) < 20:
                left_cmd = 0
                right_cmd = 0

        if self.last_send_left != left_cmd or self.last_send_right != right_cmd:
            self.last_send_left = left_cmd
            self.last_send_right = right_cmd
            self._send_command_to_motors(left_cmd, right_cmd)

    def _send_command_to_motors(self, left, right):
        self.a_star.motors(left, right)
        if left == 0 and right == 0:
            self.odometer.stop_tracking()
            self.pid_left.reset()
            self.pid_right.reset()
