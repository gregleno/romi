from a_star import AStar
from motors import Motors
import logging
import time

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
        self.log = logging.getLogger('romi')
        self.log.info("Battery: {} mV".format(self.a_star.read_battery_millivolts()))

    def move(self, left, right):
        self.motors.move(left, right)

    def stop(self):
        self.motors.move(0, 0)

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
            sleep(0.4)
