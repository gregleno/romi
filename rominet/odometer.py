import time
from collections import deque
from threading import Thread, Event
from math import pi, cos, sin


# Function bound_angle(angle) takes any angle as "angle" and returns the
# equivalent angle bound within 0 <= angle < 2 * Pi
def bound_angle(angle):
    return angle % (2 * pi)


# width between wheels in millimeters
WHEEL_DISTANCE_MM = 142.5
# Distance travelled for per encoder click in millimeters
DISTANCE_PER_TICK_MM = .152505


class Odometer(object):
    thread = None

    def __init__(self, encoders):
        self.encoders = encoders
        self.thread = None
        self.tracking = Event()
        self.tracking.clear()
        self.odom_measurement_callback = None
        self.freq = 50
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_s = 0
        self.fifo = deque(maxlen=1000)
        self.fifo.appendleft((0, 0, 0, 0, 0, 0, 0, 0, 0))

        if Odometer.thread is None:
            thread = Thread(target=self._tracking_thread)
            thread.daemon = True
            thread.start()

    def _update(self):
        encoder_left, encoder_right = self.encoders.read_encoders()
        current_time = time.time()

        last_time_s, x, y, yaw, omega, dist, speed_l, speed_r, velocity = self.fifo[0]
        delta_time_s = current_time - self.last_time_s
        delta_count_left = encoder_left - self.last_count_left
        delta_count_right = encoder_right - self.last_count_right

        if self.last_time_s != 0:
            dist_left = delta_count_left * DISTANCE_PER_TICK_MM / 1000.
            dist_right = delta_count_right * DISTANCE_PER_TICK_MM / 1000.
            distance_center = (dist_left + dist_right) / 2.
            dist += distance_center

            x += distance_center * cos(yaw)
            y += distance_center * sin(yaw)

            delta_yaw = (dist_left - dist_right) / WHEEL_DISTANCE_MM * 1000.
            yaw = bound_angle(yaw + delta_yaw)
            omega = delta_yaw / delta_time_s

            speed_l = delta_count_left / delta_time_s
            speed_r = delta_count_right / delta_time_s
            velocity = (delta_count_left + delta_count_right) / delta_time_s

            self.fifo.appendleft((current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity))

        self.last_time_s = current_time
        has_moved = self.last_count_left != encoder_left and self.last_count_right != encoder_right
        self.last_count_left = encoder_left
        self.last_count_right = encoder_right

        if self.odom_measurement_callback is not None:
            self.odom_measurement_callback(speed_l, speed_r,
                                           x, y, yaw, omega, dist,
                                           current_time)

        return has_moved

    def set_odom_measurement_callback(self, cb):
        self.odom_measurement_callback = cb

    def reset_odometry(self):
        self.fifo.clear()
        self.last_time_s = 0
        self.fifo.appendleft((0, 0, 0, 0, 0, 0, 0, 0, 0))

    def get_position_xy(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return x, y

    def get_distance(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return dist

    def get_yaw(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return yaw

    def get_omega(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return omega

    def get_speed(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return velocity

    def get_speed_left_right(self):
        (current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity) = self.fifo[0]
        return speed_l, speed_r

    def _tracking_thread(self):
        last_move_time = 0
        self.tracking.wait()
        self.reset_odometry()
        while True:
            if self._update():
                last_move_time = time.time()
            else:
                if time.time() - last_move_time > 10:
                    self.tracking.wait()
                    last_move_time = time.time()
            time.sleep(1. / self.freq)

    def stop_tracking(self):
        self.tracking.clear()

    def track_odometry(self, freq=50):
        self.freq = freq
        self.tracking.set()
