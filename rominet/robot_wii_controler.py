import cwiid
import time
import logging
from wiiremote import WiiRemote
from robot import Robot
import math


class RobotWiiControler:

    def __init__(self, robot):
        self.log = logging.getLogger('romi')
        self.robot = robot
        self.robot.play_welcome_message()
        self.wiimote = WiiRemote.connect()
        self.nun_btn_z = False

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
            self.wiimote = None
        self.robot.stop()

    def buttons_cb(self, buttons):
        if buttons & cwiid.BTN_1 and buttons & cwiid.BTN_B:
            self.release()

    def nun_buttons_cb(self, buttons):
        self.nun_btn_z = buttons & cwiid.NUNCHUK_BTN_Z
        self._move_robot(self.wiimote.get_nun_stick())

    def nun_stick_cb(self, stick):
        self._move_robot(stick)

    def _move_robot(self, stick):
        x = stick[0]
        y = stick[1]
        left = right = 0
        speed = math.sqrt(y * y + x * x)
        left = speed
        right = speed
        if speed < 0.05:
            left = right = 0
        elif abs(y) < abs(x):
            if x > 0:
                right = -speed
            else:
                left = -speed
        else:
            if y > 0:
                left = speed - max(0, -x)
                right = speed - max(0, x)
            else:
                left = -speed + max(0, -x)
                right = -speed + max(0, x)

        if not self.nun_btn_z:
            left *= 0.4
            right *= 0.4
        self.robot.move(left, right)
        pass


def main():
    log = logging.getLogger('romi')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    robot = Robot()
    rwc = RobotWiiControler(robot)

if __name__ == "__main__":
    main()
