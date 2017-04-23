#!/usr/bin/env python

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
        self.control_robot_with_buttons = False

        if self.wiimote is not None:
            self.log.info("Connected to wiimote")
            self.wiimote.set_callbacks(self.buttons_cb, self.nun_buttons_cb, self.nun_stick_cb,
                                       self.nun_stick_disconnected_cb)
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
        else:
            self._move_robot_with_buttons(buttons)

    def nun_buttons_cb(self, buttons):
        self.nun_btn_z = buttons & cwiid.NUNCHUK_BTN_Z
        self._move_robot_with_stick(self.wiimote.get_nun_stick())

    def nun_stick_cb(self, stick):
        self._move_robot_with_stick(stick)

    def nun_stick_disconnected_cb(self):
        self.robot.move(0, 0)

    def _move_robot_with_stick(self, stick):
        x = stick[0]
        y = stick[1]
        left = right = 0
        speed = math.sqrt(y * y + x * x)
        left = speed
        right = speed
        if speed < 0.001:
            left = right = 0
        elif abs(y) < abs(x) / 2:
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

    def _move_robot_with_buttons(self, buttons):
        speed = 0.3
        if buttons & (cwiid.BTN_RIGHT | cwiid.BTN_DOWN | cwiid.BTN_UP | cwiid.BTN_LEFT):
            self.control_robot_with_buttons = True

        if (buttons & cwiid.BTN_RIGHT) and (buttons & cwiid.BTN_DOWN):
            print "{}".format(cwiid.BTN_RIGHT | cwiid.BTN_DOWN)
            self.robot.move(speed, 0)
        elif (buttons & cwiid.BTN_RIGHT) and (buttons & cwiid.BTN_UP):
            self.robot.move(0, speed)
        elif (buttons & cwiid.BTN_LEFT) and (buttons & cwiid.BTN_UP):
            self.robot.move(0, -speed)
        elif (buttons & cwiid.BTN_LEFT) and (buttons & cwiid.BTN_DOWN):
            self.robot.move(-speed, 0)
        elif buttons & cwiid.BTN_RIGHT:
            self.robot.move(speed, speed)
        elif buttons & cwiid.BTN_LEFT:
            self.robot.move(-speed, -speed)
        elif buttons & cwiid.BTN_UP:
            self.robot.move(-speed, speed)
        elif buttons & cwiid.BTN_DOWN:
            self.robot.move(speed, -speed)
        else:
            if self.control_robot_with_buttons:
                self.control_robot_with_buttons = False
                self.robot.move(0, 0)


def main():
    log = logging.getLogger('romi')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    robot = Robot()
    rwc = RobotWiiControler(robot)

if __name__ == "__main__":
    main()
