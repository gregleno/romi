import logging
import time
from a_star import AStar
from motors import Motors
from camera import Camera
from odometer import Odometer
from encoders import Encoders

NO_LED = (0, 0, 0)
ALL_LEDS = (1, 1, 1)
LED1 = (1, 0, 0)
LED2 = (0, 1, 0)
LED3 = (0, 0, 1)


class Robot(object):

    def __init__(self, a_star=None):
        self.a_star = a_star or AStar()
        self.encoders = Encoders(self.a_star)
        self.odometer = Odometer(self.encoders)
        self.motors = Motors(self.a_star, self.odometer)

        self.camera = Camera()
        self.log = logging.getLogger('romi')

        self.motors.stop()

    def set_speed_target(self, left, right):
        self.motors.set_speed_target(left, right)

    def stop(self):
        if self.is_romi_board_connected():
            self.motors.stop()

    def get_camera_frame(self):
        return self.camera.get_camera_frame()

    def read_buttons(self):
        return self.a_star.read_buttons()

    def play_welcome_message(self):
        pattern = (LED1, LED2, LED3, LED1, LED2, LED3, NO_LED, ALL_LEDS, NO_LED, ALL_LEDS, NO_LED)
        for leds in pattern:
            self.a_star.leds(*leds)
            time.sleep(0.2)

    def play_goodbye_message(self):
        pattern = (ALL_LEDS, (1, 1, 0), (1, 0, 0), NO_LED)
        for leds in pattern:
            self.a_star.leds(*leds)
            time.sleep(0.4)

    def get_position_xy(self):
        situation = self.odometer.get_situation()
        return situation.x, situation.y

    def get_encoders(self):
        return self.encoders.read_encoders()

    def get_yaw(self):
        return self.odometer.get_situation().yaw

    def get_distance(self):
        return self.odometer.get_situation().dist

    def get_speed(self):
        return self.odometer.get_situation().dist

    def set_leds(self, red, yellow, green):
        self.a_star.leds(red, yellow, green)

    def reset_odometry(self):
        self.odometer.reset_odometry()

    def play_notes(self, notes):
        self.a_star.play_notes(notes)

    def get_battery(self):
        try:
            mv, = self.a_star.read_battery_millivolts()
            return mv
        except IOError:
            return None

    def is_romi_board_connected(self):
        try:
            self.a_star.read_battery_millivolts()
            return True
        except IOError:
            return False

    def rotate(self, angle, speed):
        speed = self._cap(speed)
        self.motors.rotate(angle, speed)

    def move_forward(self, distance, speed):
        speed = self._cap(speed)
        self.motors.move_forward(distance, speed)

    def _cap(self, x):
        if x > 1:
            return 1
        if x < -1:
            return -1
        return x
