import logging
import time
from threading import Thread
from rominet.a_star import AStar
from rominet.motors import Motors
from rominet.odometer import Odometer
from encoders import Encoders

NO_LED = (0, 0, 0)
ALL_LEDS = (1, 1, 1)
LED1 = (1, 0, 0)
LED2 = (0, 1, 0)
LED3 = (0, 0, 1)


class Robot:

    def __init__(self):
        # TODO: check if a star is available
        self.a_star = AStar()
        self.motors = Motors(self.a_star)
        self.encoders = Encoders(self.a_star)
        self.odometer = Odometer(self.encoders)

        self.log = logging.getLogger('romi')
        self.alive = True
        self.battery_millivolts = 0
        t = Thread(target=self._monitor_status)
        t.daemon = True
        t.start()

    def move(self, left, right):
        self.odometer.track_odometry(100)
        self.motors.move(left, right)

    def stop(self):
        self.odometer.stop_tracking()
        self.alive = False
        if self.is_romi_board_connected():
            self.motors.stop()

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

    def get_position_XY(self):
        return self.odometer.get_position_XY()

    def get_encoders(self):
        return self.encoders.get_encoder_values()

    def get_yaw(self):
        return self.odometer.get_yaw()

    def get_distance(self):
        return self.odometer.get_distance()

    def get_speed(self):
        return self.odometer.get_speed()

    def get_max_speed_left_right(self):
        return self.odometer.get_max_speed_left_right()

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
            mv, = self.a_star.read_battery_millivolts()
            return True
        except IOError:
            return False

    def _monitor_status(self):
        old_dist = 0
        old_pos = (0, 0)
        while self.alive:
            try:
                pos = self.get_position_XY()
                dist = self.get_distance()
                if old_pos != pos or old_dist != dist:
                    self.log.info("X,Y = {} dist={}".format(pos, dist))
                    old_dist = dist
                    old_pos = pos

                battery, = self.a_star.read_battery_millivolts()
                if abs(self.battery_millivolts - battery) > 50:
                    self.log.info("Battery: {} mV".format(battery))
                    self.battery_millivolts = battery
            except IOError:
                pass
            time.sleep(2)
