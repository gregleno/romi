import cwiid
import threading
import time
import logging


class WiiRemote:

    def __init__(self, wm):
        self.btn1 = False
        self.btn2 = False
        self.btnA = False
        self.btnB = False
        self.btnC = False
        self.btnZ = False
        self.btnUp = False
        self.btnDown = False
        self.btnLeft = False
        self.btnRight = False
        self.active = True
        self.wm = wm
        self.stickH = 0
        self.stickV = 0

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

    def _robotRemote(self, freq):

        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_NUNCHUK

        nunHRange = 222. - 22.
        nunHCenter = 122.
        nunVRange = 231. - 38.
        nunVCenter = 134.

        while self.active:
            buttons = self.wm.state['buttons']
            nunAcc = self.wm.state['nunchuk']['acc']
            nunButtons = self.wm.state['nunchuk']['buttons']
            nunStick = self.wm.state['nunchuk']['stick']

            nunStickH, nunStickV = nunStick

            self.stickH = (float(nunStickH) - nunHCenter) / nunHRange
            self.stickV = (float(nunStickV) - nunVCenter) / nunVRange

            if buttons & cwiid.BTN_A:
                self.btnA = True
            else:
                self.btnA = False
            if nunButtons & cwiid.NUNCHUK_BTN_Z:
                self.btnZ = True
            else:
                self.btnZ = False
            time.sleep(1 / freq)

    def _release(self):
        self.active = False
        self.wm.rumble = True
        time.sleep(.2)
        self.wm.rumble = False

    def monitor(self, freq):
        thread1 = threading.Thread(target=self._robotRemote, args=[freq])
        thread1.start()

    def release(self):
        if self.active:
            thread2 = threading.Thread(target=self._release, args=[])
            thread2.start()

    def setLed(self, led):
        self.wm.led = led

    def getLed(self):
        return self.wm.led
