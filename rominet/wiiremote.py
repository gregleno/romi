from threading import Thread
import time
import logging
import sys
import cwiid


class WiiRemote(object):

    def __init__(self, wm):
        self.buttons = sys.maxint
        self.nun_buttons = sys.maxint
        self.nun_stick = (sys.maxint, sys.maxint)
        self.active = False

        self.buttons_cb = None
        self.nun_buttons_cb = None
        self.nun_stick_cb = None
        self.nun_stick_disconnected_cb = None

        self.wm = wm
        self.led = 0
        self.nun_connected = False

        # TODO: read calibration from a calibration file
        self.calibration_ongoing = False
        self.nun_stick_max_x = 236
        self.nun_stick_min_x = 29
        self.nun_stick_max_y = 226
        self.nun_stick_min_y = 33
        self.nun_stick_center_x = 131
        self.nun_stick_center_y = 128

        self.log = logging.getLogger('romi')

    def set_callbacks(self, buttons_cb, nun_buttons_cb, nun_stick_cb, nun_stick_disconnected_cb):
        self.buttons_cb = buttons_cb
        self.nun_buttons_cb = nun_buttons_cb
        self.nun_stick_cb = nun_stick_cb
        self.nun_stick_disconnected_cb = nun_stick_disconnected_cb

    def remove_callbacks(self):
        self.buttons_cb = None
        self.nun_buttons_cb = None
        self.nun_stick_cb = None

    def get_nun_stick(self):
        if self.nun_connected:
            return self._normalize_nun_stick(self.nun_stick)
        return None

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
        return None

    def _wiimote_thread(self, freq):
        # TODO: add try catch and call a release callback
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        self.wm.rumble = True
        time.sleep(0.1)
        self.wm.rumble = False
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK

        # TODO: call the callbacks the first time they are set/modified in the loop
        while self.active:
            buttons = self.wm.state['buttons']
            try:
                nun_buttons = self.wm.state['nunchuk']['buttons']
                nun_stick = self.wm.state['nunchuk']['stick']

                # When nunchuk is reconnected the first reading is discarded to avoid glicthes
                if not self.nun_connected:
                    self.nun_buttons = nun_buttons
                    self.nun_stick = nun_stick
                    self.nun_connected = True
            except KeyError:
                if self.nun_connected:
                    if self.nun_stick_disconnected_cb is not None:
                        try:
                            self.nun_stick_disconnected_cb()
                        except Exception as e:
                            self.log.error(e)

                    self.nun_connected = False

            prev_buttons = self.buttons
            prev_nun_buttons = self.nun_buttons
            prev_nun_stick = self.nun_stick

            self.buttons = buttons
            self.nun_buttons = nun_buttons
            self.nun_stick = nun_stick

            if buttons != prev_buttons:
                if self.buttons_cb is not None:
                    try:
                        self.buttons_cb(buttons)
                    except Exception as e:
                        self.log.error(e)

                if buttons & cwiid.BTN_PLUS and buttons & cwiid.BTN_MINUS and buttons & cwiid.BTN_B:
                    # If we start calibration we assume that the nunchuck is at the center
                    if not self.calibration_ongoing:
                        self._start_calibration(nun_stick)
                    else:
                        self._complete_calibration()

            if nun_buttons != prev_nun_buttons and self.nun_connected:
                if self.nun_buttons_cb is not None:
                    try:
                        self.nun_buttons_cb(nun_buttons)
                    except Exception as e:
                        self.log.error(e)

            if nun_stick != prev_nun_stick and self.nun_connected:
                # If calibration is ongoing we do not call the normal callback
                if self.calibration_ongoing:
                    self._calibration_cb(nun_stick)
                elif self.nun_stick_cb is not None:
                    try:
                        self.nun_stick_cb(self._normalize_nun_stick(nun_stick))
                    except Exception as e:
                        self.log.error(e)

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
            t = Thread(target=self._wiimote_thread, args=[freq])
            t.daemon = True
            t.start()
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

        self.log.info("Calibration started. Please move the nunchuck in all directions")
        self.log.info("Press PLUS MINUS and B to complete calibration")

        self.nun_stick_max_x = 0
        self.nun_stick_min_x = sys.maxint
        self.nun_stick_max_y = 0
        self.nun_stick_min_y = sys.maxint
        self.nun_stick_center_x = stick[0]
        self.nun_stick_center_y = stick[1]

    def _complete_calibration(self):
        self.calibration_ongoing = False
        self.log.info("Nunchuck calibration data:")
        self.log.info("  Center: %d,%d" % (self.nun_stick_center_x, self.nun_stick_center_y))
        self.log.info("  Max: %d,%d" % (self.nun_stick_max_x, self.nun_stick_max_y))
        self.log.info("  Min: %d,%d" % (self.nun_stick_min_x, self.nun_stick_min_y))

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
