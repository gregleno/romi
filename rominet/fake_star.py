import time

from rominet.motor import Motor


class FakeAStar(object):

    def __init__(self):
        self.leds = (0, 0, 0)
        self.encoders = (0, 0)
        self.cmd = (0, 0)
        self.last_encoder_update_time = 0
        pass

    def leds(self, red, yellow, green):
        self.leds = (red, yellow, green)

    def play_notes(self, notes):
        pass

    def motors(self, left, right):
        self._update_encoders()
        self.cmd = (left, right)

    def read_buttons(self):
        return 0

    def read_battery_millivolts(self):
        return 7000,

    def read_analog(self):
        return 0

    def read_encoders(self):
        self._update_encoders()
        return self.encoders

    def _update_encoders(self):
        current_time = time.time()
        delta_time = current_time - self.last_encoder_update_time
        left = self.encoders[0] + self.cmd[0] * Motor.MAX_SPEED / Motor.MAX_CMD * delta_time
        right = self.encoders[1] + self.cmd[1] * Motor.MAX_SPEED / Motor.MAX_CMD * delta_time
        self.last_encoder_update_time = current_time
        self.encoders = (left, right)
