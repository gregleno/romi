import cwiid
import threading
import time
import logging
from wiiremote import WiiRemote
from a_star import AStar

NO_LED = (0, 0, 0)
ALL_LEDS = (1, 1, 1)
LED1 = (1, 0, 0)
LED2 = (0, 1, 0)
LED3 = (0, 0, 1)


class RobotControler:

    def __init__(self):
        self.log = logging.getLogger('romi')
        self.a_star = AStar()
        self.play_welcome_message()
        self.wiimote = WiiRemote.connect()

        if self.wiimote is not None:
            self.log.info("Connected to wiimote")
            self.wiimote.set_callbacks(self.buttons_cb, self.nun_buttons_cb, self.nun_stick_cb)
            self.wiimote.monitor(100)
            self.log.info("Started")
        else:
            self.log.error("Could not connect to wiimote")

    def release(self):
        if self.wiimote is not None:
            self.wiimote.remove_callbacks()
            self.wiimote.release()

    def buttons_cb(self, buttons):
        print("buttons_cb")

    def nun_buttons_cb(self, buttons):
        print("nun_buttons_cb")

    def nun_stick_cb(self, stick):
        print("nun_stick_cb")

    def play_welcome_message(self):
        pattern = (LED1, LED2, LED3, LED1, LED2, LED3, NO_LED, ALL_LEDS, NO_LED, ALL_LEDS, NO_LED)
        for leds in pattern:
            self.a_star.leds(*leds)
            time.sleep(0.2)
