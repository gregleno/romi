import cwiid
import threading
import time
import logging


class WiiRemote:

    def __init__(self, wm):
        self.buttons = 0
        self.nun_buttons = 0
        self.nun_stick = (0, 0)
        self.active = True
        self.buttons_cb = None
        self.nun_buttons_cb = None
        self.nun_stick_cb = None
        self.wm = wm
        self.led = 0

    def set_callbacks(self, buttons_cb, nun_buttons_cb, nun_stick_cb):
        self.buttons_cb = buttons_cb
        self.nun_buttons_cb = nun_buttons_cb
        self.nun_stick_cb = nun_stick_cb

    def remove_callbacks(self):
        self.buttons_cb = None
        self.nun_buttons_cb = None
        self.nun_stick_cb = None

    @staticmethod
    def connect():
        log = logging.getLogger('romi')
        log.info("Simultaneously press Wii remote buttons 1 and 2 now")
        i = 1
        wm = None
        while wm is None:
            try:
                wm = cwiid.Wiimote()
            except RuntimeError:
                if i > 10:
                    break
                i += 1
                log.info("Failed to connect to Wii remote")
        if wm is not None:
            log.info("Wii remote successfully connected")
            wm.rumble = True
            time.sleep(.2)
            wm.rumble = False
            return WiiRemote(wm)
        else:
            return None

    def _robot_remote(self, freq):

        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        self.wm.rumble = True
        time.sleep(1)
        self.wm.rumble = False
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        while self.active:
            # Todo add mutex
            buttons = self.wm.state['buttons']
            nun_buttons = self.wm.state['nunchuk']['buttons']
            nun_stick = self.wm.state['nunchuk']['stick']

            if buttons != self.buttons and self.buttons_cb is not None:
                self.buttons_cb(buttons)
            self.buttons = buttons

            if nun_buttons != self.nun_buttons and self.nun_buttons_cb is not None:
                self.nun_buttons_cb(nun_buttons)
            self.nun_buttons = nun_buttons

            if nun_stick != self.nun_stick and self.nun_stick_cb is not None:
                self.nun_stick_cb(nun_stick)
            self.nun_stick = nun_stick

            time.sleep(1. / freq)

    def _release(self):
        self.active = False
        self.wm.rumble = True
        time.sleep(.2)
        self.wm.rumble = False

    def monitor(self, freq):
        self.active = True
        thread1 = threading.Thread(target=self._robot_remote, args=[freq])
        thread1.start()

    def release(self):
        if self.active:
            thread2 = threading.Thread(target=self._release, args=[])
            thread2.start()

    def set_led(self, led):
        self.wm.led = led
