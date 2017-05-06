import time
from threading import Thread
from math import pi, cos, sin


# Function bound_angle(angle) takes any angle as "angle" and returns the
# equivalent angle bound within 0 <= angle < 2 * Pi
def bound_angle(angle):
    return angle % (2 * pi)


def current_time_ms():
    return int(round(time.time() * 1000))


# width between wheels in millimeters
WHEEL_DISTANCE_MM = 142.5
# Distance travelled for per encoder click in millimeters
DISTANCE_PER_TICK_MM = .152505


# Function relative_angle(angleRef, angle) returns the shortest relative
# angle from a reference angle "angleRef" to an angle "angle". The retuned
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
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_ms = 0
        self.max_speed_left = 0
        self.max_speed_right = 0
        self.speed_left = 0
        self.speed_right = 0
        self.ticks_threshold = 10
        self.time_threshold = 200
        self.velocity = 0

    def update(self, encoder_left, encoder_right, current_time):
        delta_time_ms = current_time - self.last_time_ms
        delta_count_left = encoder_left - self.last_count_left
        delta_count_right = encoder_right - self.last_count_right

        if self.last_time_ms != 0:
            if (abs(delta_count_left) > self.ticks_threshold or
                abs(delta_count_right) > self.ticks_threshold or
                delta_time_ms > self.time_threshold):
                self.speed_left = 1000 * delta_count_left / delta_time_ms
                self.speed_right = 1000 * delta_count_right / delta_time_ms
                self.velocity = 1000 * (delta_count_left + delta_count_right) / delta_time_ms
                self.max_speed_left = max(self.max_speed_left, abs(self.speed_left))
                self.max_speed_right = max(self.max_speed_right, abs(self.speed_right))
            else:
                return

        self.last_time_ms = current_time
        self.last_count_left = encoder_left
        self.last_count_right = encoder_right


class PositionMeter(object):
    def __init__(self):
        self.last_count_left = 0
        self.last_count_right = 0
        self.last_time_ms = 0
        self.yaw = 0
        self.x = 0
        self.y = 0
        self.omega = 0
        self.dist = 0
        self.threshold = 10

    def update(self, encoder_left, encoder_right, current_time):
        delta_time_ms = current_time - self.last_time_ms
        delta_count_left = encoder_left - self.last_count_left
        delta_count_right = encoder_right - self.last_count_right

        if self.last_time_ms != 0:
            if abs(delta_count_left) > self.threshold or abs(delta_count_right) > self.threshold:
                dist_left = delta_count_left * DISTANCE_PER_TICK_MM
                dist_right = delta_count_right * DISTANCE_PER_TICK_MM
                distance_center = (dist_left + dist_right) / 2.
                self.dist += distance_center

                self.x += distance_center * cos(self.yaw)
                self.y += distance_center * sin(self.yaw)

                delta_yaw = (dist_right - dist_left) / WHEEL_DISTANCE_MM
                self.yaw = bound_angle(self.yaw + delta_yaw)
                self.omega = delta_yaw / delta_time_ms
            else:
                return

        self.last_time_ms = current_time
        self.last_count_left = encoder_left
        self.last_count_right = encoder_right


class Odometer(object):

    def __init__(self, encoders):
        self.encoders = encoders
        self.pos = PositionMeter()
        self.speedometer = Speedometer()
        self.thread = None
        self.tracking = False
        self.freq = 100

    def _update(self):
        count_left, count_right = self.encoders.read_encoders()
        time_ms = current_time_ms()
        self.speedometer.update(count_left, count_right, time_ms)
        self.pos.update(count_left, count_right, time_ms)

    def get_position_XY(self):
        return self.pos.x, self.pos.y

    def get_distance(self):
        return self.pos.dist

    def get_yaw(self):
        return self.pos.yaw

    def angle_relative_to_yaw(self, angle):
        return relative_angle(self.pos.yaw, angle)

    def get_omega(self):
        return self.pos.omega

    def get_speed(self):
        return self.speedometer.velocity

    def get_speed_left_right(self):
        return self.speedometer.speed_left, self.speedometer.speed_right

    def get_max_speed_left_right(self):
        return self.speedometer.max_speed_left, self.speedometer.max_speed_right

    def _tracking_thread(self):
        while self.tracking:
            self._update()
            time.sleep(1. / self.freq)

    def stop_tracking(self):
        self.tracking = False
        self.thread = None

    def track_odometry(self, freq=100):
        self.freq = freq
        if self.thread is None:
            self.encoders.reset()
            self.tracking = True
            self.thread = Thread(target=self._tracking_thread)
            self.thread.daemon = True
            self.thread.start()
