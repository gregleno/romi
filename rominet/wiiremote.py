import cwiid
import threading
import time
import logging
import sys


class WiiRemote:

    def __init__(self, wm):
        self.buttons = 0
        self.nun_buttons = 0
        self.nun_stick = (0, 0)
        self.active = False
        self.buttons_cb = None
        self.nun_buttons_cb = None
        self.nun_stick_cb = None
        self.wm = wm
        self.led = 0

        # TODO: read calibration from a calibration file
        self.calibration_ongoing = False
        self.nun_stick_max_x = 236
        self.nun_stick_min_x = 29
        self.nun_stick_max_y = 226
        self.nun_stick_min_y = 33
        self.nun_stick_center_x = 131
        self.nun_stick_center_y = 128

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

    def _wiimote_thread(self, freq):
        # TODO: add try catch and call a release callback
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        self.wm.rumble = True
        time.sleep(0.1)
        self.wm.rumble = False
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        while self.active:
            buttons = self.wm.state['buttons']
            nun_buttons = self.wm.state['nunchuk']['buttons']
            nun_stick = self.wm.state['nunchuk']['stick']

            if buttons != self.buttons:
                if self.buttons_cb is not None:
                    self.buttons_cb(buttons)

                if buttons & cwiid.BTN_PLUS and buttons & cwiid.BTN_MINUS and buttons & cwiid.BTN_B:
                    # If we start calibration we assume that the nunchuck is at the center
                    if not self.calibration_ongoing:
                        self._start_calibration(nun_stick)
                    else:
                        self._complete_calibration()

            self.buttons = buttons

            if nun_buttons != self.nun_buttons:
                if self.nun_buttons_cb is not None:
                    self.nun_buttons_cb(nun_buttons)
                self.nun_buttons = nun_buttons

            if nun_stick != self.nun_stick:
                # If calibration is ongoing we do not call the normal callback
                if self.calibration_ongoing:
                    self._calibration_cb(nun_stick)
                elif self.nun_stick_cb is not None:
                    self.nun_stick_cb(self._normalize_nun_stick(nun_stick))
                self.nun_stick = nun_stick

            time.sleep(1. / freq)

    def release(self):
        self.active = False
        if self.wm is not None:
            self.wm.rumble = True
            time.sleep(.1)
            self.wm.rumble = False
            self.wm.close()

    def monitor(self, freq):
        if not self.active:
            self.active = True
            thread1 = threading.Thread(target=self._wiimote_thread, args=[freq])
            thread1.start()
        else:
            raise Exception("Wiiremote already active")

    def _start_calibration(self, stick):
        self.calibration_ongoing = True
        self.wm.rumble = True
        time.sleep(.1)
        self.wm.rumble = False
        time.sleep(.1)
        self.wm.rumble = True
        time.sleep(.1)
        self.wm.rumble = False

        log.info("Calibration started. Please move the nunchuck in all directions")
        log.info("Press PLUS MINUS and B to complete calibration")

        self.nun_stick_max_x = 0
        self.nun_stick_min_x = sys.maxint
        self.nun_stick_max_y = 0
        self.nun_stick_min_y = sys.maxint
        self.nun_stick_center_x = stick[0]
        self.nun_stick_center_y = stick[1]

    def _complete_calibration(self):
        self.calibration_ongoing = False
        log.info("Nunchuck calibration data:")
        log.info("  Center: %d,%d" % (self.nun_stick_center_x, self.nun_stick_center_y))
        log.info("  Max: %d,%d" % (self.nun_stick_max_x, self.nun_stick_max_y))
        log.info("  Min: %d,%d" % (self.nun_stick_min_x, self.nun_stick_min_y))

    def _calibration_cb(self, stick):
        x, y = stick
        self.nun_stick_max_x = max(x, self.nun_stick_max_x)
        self.nun_stick_max_y = max(y, self.nun_stick_max_y)
        self.nun_stick_min_x = min(x, self.nun_stick_min_x)
        self.nun_stick_min_y = min(y, self.nun_stick_min_y)

    def _normalize_nun_stick(self, stick):
        if stick[0] > self.nun_stick_center_x:
            xn = float(stick[0] - self.nun_stick_center_x) / (
                       self.nun_stick_max_x - self.nun_stick_center_x)
        else:
            xn = float(stick[0] - self.nun_stick_center_x) / (
                       self.nun_stick_center_x - self.nun_stick_min_x)

        if stick[1] > self.nun_stick_center_y:
            yn = float(stick[1] - self.nun_stick_center_y) / (
                       self.nun_stick_max_y - self.nun_stick_center_y)
        else:
            yn = float(stick[1] - self.nun_stick_center_y) / (
                       self.nun_stick_center_y - self.nun_stick_min_y)

        return (xn, yn)

    def set_led(self, led):
        self.wm.led = led
