import time
from collections import deque, namedtuple
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

Pos = namedtuple("Pos", ("x", "y", "speed_left", "speed_right", "yaw", "omega", "dist", "speed", "time"))


# Function relative_angle(angleRef, angle) returns the shortest relative
# angle from a reference angle "angleRef" to an angle "angle". The returned
# relative angle is bound within -Pi < angle < Pi
def relative_angle(angle_ref, angle):
    angle_ref = bound_angle(angle_ref)
    angle = bound_angle(angle)

    if angle - angle_ref > pi:
        ret = angle - angle_ref - 2 * pi
    elif angle - angle_ref < -pi:
        ret = angle - angle_ref + 2 * pi
    else:
        ret = angle - angle_ref

    return ret


class Speedometer(object):
    def __init__(self):
        self.speed_left = 0
        self.speed_right = 0
        self.velocity = 0
        self.fifo = deque(maxlen=10)

    def reset(self):
        self.fifo.clear()
        self.speed_left = 0
        self.speed_right = 0
        self.velocity = 0

    def update(self, encoder_left, encoder_right, current_time):
        self.fifo.append((current_time, encoder_left, encoder_right))

        (last_time_s, last_count_left, last_count_right) = self.fifo[0]
        delta_time_s = current_time - last_time_s
        delta_count_left = encoder_left - last_count_left
        delta_count_right = encoder_right - last_count_right

        if delta_time_s != 0:
            self.speed_left = delta_count_left / delta_time_s
            self.speed_right = delta_count_right / delta_time_s
            self.velocity = (delta_count_left + delta_count_right) / delta_time_s


class PositionMeter(object):
    def __init__(self):
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_s = 0
        self.dist = 0
        self.fifo = deque([(time.time(), 0, 0, 0, 0, 0)], maxlen=1000)

    def reset(self):
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_s = 0
        self.dist = 0
        self.fifo = deque([(time.time(), 0, 0, 0, 0, 0)], maxlen=1000)

    def update(self, encoder_left, encoder_right, current_time):
        delta_time_s = current_time - self.last_time_s
        delta_count_left = encoder_left - self.last_count_left
        delta_count_right = encoder_right - self.last_count_right
        last_time_s, x, y, yaw, omega, dist = self.fifo[0]

        if self.last_time_s != 0:
            dist_left = delta_count_left * DISTANCE_PER_TICK_MM / 1000.
            dist_right = delta_count_right * DISTANCE_PER_TICK_MM / 1000.
            distance_center = (dist_left + dist_right) / 2.
            self.dist += distance_center

            x += distance_center * cos(yaw)
            y += distance_center * sin(yaw)

            delta_yaw = (dist_right - dist_left) / WHEEL_DISTANCE_MM * 1000.
            yaw = bound_angle(yaw + delta_yaw)
            omega = delta_yaw / delta_time_s

            self.fifo.appendleft((current_time, x, y, yaw, omega, self.dist))

        self.last_time_s = current_time
        has_moved = self.last_count_left != encoder_left and self.last_count_right != encoder_right
        self.last_count_left = encoder_left
        self.last_count_right = encoder_right
        return has_moved

    def get_xy(self):
        (current_time, x, y, yaw, omega, dist) = self.fifo[0]
        return x, y

    def get_yaw(self):
        (current_time, x, y, yaw, omega, dist) = self.fifo[0]
        return yaw

    def get_omega(self):
        (current_time, x, y, yaw, omega, dist) = self.fifo[0]
        return omega

    def get_pos(self):
        return self.fifo[0]


class Odometer(object):
    thread = None

    def __init__(self, encoders):
        self.encoders = encoders
        self.pos = PositionMeter()
        self.speedometer = Speedometer()
        self.thread = None
        self.tracking = Event()
        self.tracking.clear()
        self.odom_measurement_callback = None
        self.freq = 50
        if Odometer.thread is None:
            thread = Thread(target=self._tracking_thread)
            thread.daemon = True
            thread.start()

    def _update(self):
        count_left, count_right = self.encoders.read_encoders()
        time_s = time.time()
        has_moved = self.pos.update(count_left, count_right, time_s)
        self.speedometer.update(count_left, count_right, time_s)
        if self.odom_measurement_callback is not None:
            current_time, x, y, yaw, omega, dist = self.pos.get_pos()
            self.odom_measurement_callback(self.speedometer.speed_left,
                                           self.speedometer.speed_right,
                                           x, y, yaw, omega, dist,
                                           time_s)

        return has_moved

    def set_odom_measurement_callback(self, cb):
        self.odom_measurement_callback = cb

    def reset_odometry(self):
        self.speedometer.reset()
        self.pos.reset()

    def get_position_xy(self):
        return self.pos.get_xy()

    def get_distance(self):
        return self.pos.dist

    def get_yaw(self):
        return self.pos.get_yaw()

    def angle_relative_to_yaw(self, angle):
        return relative_angle(self.pos.get_yaw(), angle)

    def get_omega(self):
        return self.pos.get_omega()

    def get_speed(self):
        return self.speedometer.velocity

    def get_speed_left_right(self):
        return self.speedometer.speed_left, self.speedometer.speed_right

    def _tracking_thread(self):
        last_move_time = 0
        self.tracking.wait()
        while True:
            if self._update():
                last_move_time = time.time()
            else:
                if time.time() - last_move_time > 2:
                    self.tracking.wait()
                    last_move_time = time.time()
            time.sleep(1. / self.freq)

    def stop_tracking(self):
        self.tracking.clear()

    def track_odometry(self, freq=50):
        self.freq = freq
        self.tracking.set()
