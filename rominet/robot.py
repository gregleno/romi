from a_star import AStar
from motors import Motors
from odometer import Odometer
from encoders import Encoders
import logging
import time
from threading import Thread

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
        self.motors.stop()
        self.odometer.stop_tracking()
        self.alive = False

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

    def _monitor_status(self):
        while self.alive:
            try:
                battery, = self.a_star.read_battery_millivolts()
                if abs(self.battery_millivolts - battery) > 50:
                    self.log.info("Battery: {} mV".format(battery))
                    self.battery_millivolts = battery
            except:
                pass
            time.sleep(2)
