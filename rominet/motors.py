from rominet.pid import PID
import logging
from math import pi
from collections import namedtuple


DistanceCommand = namedtuple("DistanceCommand", ("distance", "yaw", "speed", "initial_distance"))
RotationCommand = namedtuple("RotationCommand", ("yaw", "speed"))
SpeedCommand = namedtuple("SpeedCommand", ("left", "right"))
count = 0


class Motors(object):

    def __init__(self, a_star, odometer):
        self.a_star = a_star
        self.max_cmd = 400.
        self.max_speed = float(1440 * 150 / 60.)  # 1440 ticks per rev, 150 rev per min 60 sec per minute
        self.odometer = odometer
        self.pid_speed_left = PID(0.1, 5, 0, self.max_speed)
        self.pid_speed_right = PID(0.1, 5, 0, self.max_speed)
        self.pid_distance = PID(20, 0, 0.0, self.max_speed)
        self.pid_yaw_correction = PID(1, 2, 0.0, 1)
        self.pid_rotation_angle = PID(1, 0.00, 0, 2 * pi) # max 1 revolution per second
        self.pid_rotation_speed = PID(800, 3000, 0, self.max_speed)
        self.last_speed_cmd_left = 0
        self.last_speed_cmd_right = 0

        self.distance_command = None
        self.rotation_command = None
        self.speed_command = None
        self.command_reached = True

        self.last_send_left = -1000
        self.last_send_right = -1000
        self.a_star.motors(0, 0)
        self.odometer.set_odom_measurement_callback(self._odom_measurement_callback)
        self.log = logging.getLogger('romi')

    def convert_command_to_speed(self, x):
        return self.cap(x, 1) * self.max_speed

    @staticmethod
    def cap(x, max_value):
        if x > max_value:
            x = max_value
        if x < -max_value:
            x = -max_value
        return x

    @staticmethod
    def min_abs_value(x, min_value):
        if 0 < x < min_value:
            x = min_value
        if -min_value < x < 0:
            x = -min_value
        return x

    def set_speed_target(self, left, right):
        self.distance_command = None
        self.rotation_command = None
        self.command_reached = False
        self.speed_command = SpeedCommand(self.convert_command_to_speed(left), self.convert_command_to_speed(right))
        if left == 0 and right == 0:
            self.reset_pids()
            self.odometer.stop_tracking()
        else:
            self.odometer.track_odometry()

    def move_forward(self, distance, speed):
        print("move_forward")
        self.rotation_command = None
        self.speed_command = None
        self.distance_command = DistanceCommand(distance, self.odometer.get_yaw(),
                                                self.convert_command_to_speed(speed), self.odometer.get_distance())
        self.reset_pids()
        self.command_reached = False
        self.odometer.track_odometry()

    def rotate(self, angle, speed):
        print("rotate {}:{}".format(angle, speed))
        self.distance_command = None
        self.speed_command = None
        self.rotation_command = RotationCommand((self.odometer.get_yaw() + angle) % (2 * pi), speed)
        self.command_reached = False
        self.reset_pids()
        self.odometer.track_odometry()

    def stop(self):
        print("stop")
        self.distance_command = None
        self.rotation_command = None
        self.speed_command = None
        self.command_reached = True
        self._send_command_to_motors(0, 0)
        self.reset_pids()

    def _odom_measurement_callback(self, speed_left, speed_right, x, y, yaw, omega, dist, current_time):
        global count
        count += 1

        delta = 0
        if self.distance_command is not None:
            set_point_distance = self.distance_command.distance + self.distance_command.initial_distance
            set_point_yaw = self.distance_command.yaw
            max_speed = self.distance_command.speed
            if abs(dist - set_point_distance) < 0.01 \
                    or abs(self.distance_command.initial_distance - dist) - abs(self.distance_command.distance) > 0.00 \
                    or self.command_reached:
                self.odometer.stop_tracking()
                self.command_reached = True
                speed_cmd = 0
            else:
                speed_cmd = self.pid_distance.get_output(set_point_distance * 1000, dist * 1000, current_time)
                last_speed_cmd = (self.last_speed_cmd_left + self.last_speed_cmd_right) / 2
                max_acc = self.max_speed / 5
                if speed_cmd - last_speed_cmd > max_acc:
                    speed_cmd = last_speed_cmd + max_acc
                elif last_speed_cmd - speed_cmd > max_acc:
                    speed_cmd = last_speed_cmd - max_acc

                # Set max speed
                speed_cmd = max(min(speed_cmd, max_speed), -max_speed)

                # Set min value
                speed_cmd = self.min_abs_value(speed_cmd, 8)

            delta = self._get_yaw_delta(set_point_yaw, yaw, self.pid_yaw_correction, current_time)

            # going backward, right and left motors have an inverted effect on rotation
            if speed_cmd < 0:
                delta = -delta

            set_point_speed_left = speed_cmd
            set_point_speed_right = speed_cmd
            #print("yaw: {} set_point_yaw:{}".format(convert_to_deg(yaw), convert_to_deg(set_point_yaw)))
            #print("speed_cmd:{}".format(int(speed_cmd/self.max_speed*100)))

        elif self.rotation_command is not None:
            set_point_yaw = self.rotation_command.yaw

            if abs(convert_to_deg(yaw - set_point_yaw)) < 0.5 or self.command_reached:
                self.odometer.stop_tracking()
                self.command_reached = True
                speed_cmd = 0
            else:
                rotation_speed = self._get_yaw_delta(set_point_yaw, yaw, self.pid_rotation_angle, current_time)
                rotation_speed = self.cap(rotation_speed, self.rotation_command.speed)
                speed_cmd = self.pid_rotation_speed.get_output(rotation_speed, omega, current_time)
                last_speed_cmd = self.last_speed_cmd_left
                max_acc = self.max_speed / 5
                if speed_cmd - last_speed_cmd > max_acc:
                    speed_cmd = last_speed_cmd + max_acc
                elif last_speed_cmd - speed_cmd > max_acc:
                    speed_cmd = last_speed_cmd - max_acc
            #print("rotation_speed: {} speed_cmd:{}".format(rotation_speed, speed_cmd))
            # Set min value
            # speed_cmd = self.min_abs_value(set_point_speed * speed_cmd_delta, 100)

            set_point_speed_left = speed_cmd
            set_point_speed_right = -speed_cmd
            #print("speed_cmd_delta: {}".format(speed_cmd))
            # print("yaw: {} set_yaw:{} omega:{}".format(convert_to_deg(yaw), convert_to_deg(set_point_yaw), convert_to_deg(omega)))

        elif self.speed_command is not None:
            set_point_speed_left = self.speed_command.left
            set_point_speed_right = self.speed_command.right

        else:
            set_point_speed_left = 0
            set_point_speed_right = 0

        set_point_speed_left = set_point_speed_left * (1 + delta / 2.)
        set_point_speed_right = set_point_speed_right * (1 - delta / 2.)

        left_speed_cmd = self.pid_speed_left.get_output(set_point_speed_left, speed_left, current_time)
        right_speed_cmd = self.pid_speed_right.get_output(set_point_speed_right, speed_right, current_time)

        self.last_speed_cmd_left, self.last_speed_cmd_right = left_speed_cmd, right_speed_cmd

        left_cmd = int(left_speed_cmd * self.max_cmd / self.max_speed)
        #if left_cmd != 0:
        #    left_cmd = self.min_abs_value(left_cmd, 16)

        right_cmd = int(right_speed_cmd * self.max_cmd / self.max_speed)
        #if right_cmd != 0:
        #    right_cmd = self.min_abs_value(right_cmd, 16)

        #if set_point_speed_left != 0 or set_point_speed_right != 0:
            #print("speedl: {} speedr: {}".format(int(speed_left/self.max_speed*100), int(speed_right/self.max_speed*100)))
            #print("set_point_speed_left: {} set_point_speed_right: {}".format(int(set_point_speed_left/self.max_speed*100),
            #                                                                  int(set_point_speed_right/self.max_speed*100)))
            #print("left_cmd: {} right_cmd: {}".format(int(left_cmd/self.max_cmd*100), int(right_cmd/self.max_cmd*100)))
        if count % 25 == 0:
            print("yaw: {} ".format(int(yaw * 180. / pi*10)/10.))
            print("dist: {} x:{} y:{} \n".format(int(dist*1000)/1000., int(x*1000)/1000., int(y*1000)/1000.))
        if set_point_speed_left == 0 and set_point_speed_right == 0:
            if abs(left_cmd) < 20 and abs(right_cmd) < 20:
                left_cmd = 0
                right_cmd = 0

        # if left_cmd != 0 or set_point_speed_right != 0:
        #    print("left_cmd: {} right_cmd: {}".format(int(left_cmd/self.max_cmd*100), int(right_cmd/self.max_cmd*100)))
        self._send_command_to_motors(left_cmd, right_cmd)

    def _send_command_to_motors(self, left, right):
        self.last_send_left = left
        self.last_send_right = right
        self.a_star.motors(left, right)

    def _get_yaw_delta(self, set_point_yaw, yaw, pid, current_time):
        if set_point_yaw - yaw > pi:
            yaw = yaw + 2 * pi
        elif set_point_yaw - yaw < -pi:
            yaw = yaw - 2 * pi
        return pid.get_output(set_point_yaw, yaw, current_time)

    def reset_pids(self):
        self.pid_speed_left.reset()
        self.pid_speed_right.reset()
        self.pid_distance.reset()
        self.pid_yaw_correction.reset()
        self.pid_rotation_angle.reset()
        self.pid_rotation_speed.reset()



def convert_to_deg(x):
    return x * 180. / pi