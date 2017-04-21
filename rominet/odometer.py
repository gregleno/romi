import time
from math import pi, cos, sin


# Function bound_angle(angle) takes any angle as "angle" and returns the
# equivalent angle bound within 0 <= angle < 2 * Pi
def bound_angle(angle):
    return angle % (2 * pi)


# Function relative_angle(angleRef, angle) returns the shortest relative
# angle from a reference angle "angleRef" to an angle "angle". The retuned
# relative angle is bound within -Pi < angle < Pi
def relative_angle(angle_ref, angle):
    angle_ref = bound_angle(angleRef)
    angle = bound_angle(angle)

    if angle - angle_ref > pi:
        relative_angle = angle - angle_ref - 2 * pi
    elif angle - angle_ref < -pi:
        relative_angle = angle - angle_ref + 2 * pi
    else:
        relative_angle = angle - angle_ref

    return relative_angle


class Odometer:

    def __init__(self, encoders, time_step=.02):
        self.encoders = encoders
        self.time_step = time_step

        # width between wheels in millimeters
        self.wheel_distance_mm = 142.5
        # Distance travelled for per encoder click in millimeters
        self.distance_per_tick_mm_mm = .152505

        self.last_count_left = 0
        self.last_count_right = 0
        self.speed_left = 0
        self.speed_right = 0
        self.phi = 0
        self.x = 0
        self.y = 0
        self.v = 0
        self.omega = 0
        self.dist = 0

    def update(self):

        count_left, count_right = self.encoders.read_encoders()

        delta_count_left = count_left - self.last_count_left
        delta_count_right = count_right - self.last_count_right

        dist_left = delta_count_left * self.distance_per_tick_mm
        dist_right = delta_count_right * self.distance_per_tick_mm
        distance_center = (dist_left + dist_right) / 2.
        self.dist += distance_center

        self.x += distance_center * cos(self.phi)
        self.y += distance_center * sin(self.phi)

        delta_phi = (dist_right - dist_left) / self.wheel_distance_mm
        self.phi = bound_angle(self.phi + delta_phi)

        # TODO: Use current time to compute speed
        self.speed_left = dist_left / self.time_step
        self.speed_right = dist_right / self.time_step
        self.v = distance_center / self.time_step
        self.omega = delta_phi / self.time_step

        self.last_count_left = count_left
        self.last_count_right = count_right

    def get_position_XY(self):
        return self.x, self.y

    def get_phi(self):
        return self.phi

    def angle_relative_to_phi(self, angle):
        return relative_angle(self.phi, angle)

    def get_omega(self):
        return self.omega

    def get_speed(self):
        return self.v

    def getspeed_left_right(self):
        return self.speed_left, self.speed_right
