import time
from collections import deque
from threading import Thread, Event
from math import pi, cos, sin

from rominet.situation import Situation


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
        self.odom_measurement_callback = []
        self.freq = 50
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_s = 0
        self.fifo = deque(maxlen=1000)
        self.fifo.appendleft(Situation(0, 0, 0, 0, 0, 0, 0, 0, 0))

        if Odometer.thread is None:
            thread = Thread(target=self._tracking_thread)
            thread.daemon = True
            thread.start()

    def _update(self):
        encoder_left, encoder_right = self.encoders.read_encoders()
        current_time = time.time()

        last_situation = self.fifo[0]

        delta_time_s = current_time - self.last_time_s
        delta_count_left = encoder_left - self.last_count_left
        delta_count_right = encoder_right - self.last_count_right

        if not self.last_time_s:
            situation = last_situation
        else:
            dist_left = delta_count_left * DISTANCE_PER_TICK_MM / 1000.
            dist_right = delta_count_right * DISTANCE_PER_TICK_MM / 1000.
            distance_center = (dist_left + dist_right) / 2.
            dist = last_situation.dist + distance_center

            x = last_situation.x + distance_center * cos(last_situation.yaw)
            y = last_situation.y + distance_center * sin(last_situation.yaw)

            delta_yaw = (dist_left - dist_right) / WHEEL_DISTANCE_MM * 1000.
            yaw = bound_angle(last_situation.yaw + delta_yaw)
            omega = delta_yaw / delta_time_s

            speed_l = delta_count_left / delta_time_s
            speed_r = delta_count_right / delta_time_s
            velocity = (delta_count_left + delta_count_right) / delta_time_s

            situation = Situation(current_time, x, y, yaw, omega, dist, speed_l, speed_r, velocity)
            self.fifo.appendleft(situation)

        self.last_time_s = current_time
        has_moved = self.last_count_left != encoder_left or self.last_count_right != encoder_right
        self.last_count_left = encoder_left
        self.last_count_right = encoder_right

        for cb in self.odom_measurement_callback:
            cb(situation)

        return has_moved

    def add_measurement_callback(self, cb):
        self.odom_measurement_callback.append(cb)

    def reset_odometry(self):
        self.fifo.clear()
        self.last_time_s = 0
        self.fifo.appendleft(Situation(0, 0, 0, 0, 0, 0, 0, 0, 0))

    def get_situation(self):
        return self.fifo[0]

    def _tracking_thread(self):
        last_move_time = 0
        self.tracking.wait()
        self.reset_odometry()
        while True:
            current_time = time.time()
            if self._update():
                last_move_time = current_time
            elif current_time - last_move_time > 1:
                self.tracking.wait()
                last_move_time = current_time
            time.sleep(1. / self.freq)

    def stop_tracking(self):
        self.tracking.clear()

    def track_odometry(self):
        self.tracking.set()
