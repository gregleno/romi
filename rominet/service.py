#!/usr/bin/env python

import logging
from systemd.journal import JournalHandler
import time
from time import sleep
from robot import Robot
from robot_wii_controler import RobotWiiControler
import os

NO_LED = (0, 0, 0)
ALL_LEDS = (1, 1, 1)
LED1 = (1, 0, 0)
LED2 = (0, 1, 0)
LED3 = (0, 0, 1)


def main():

    robot_wii_controler = None
    robot = Robot()

    try:
        log = logging.getLogger('romi')
        log.addHandler(JournalHandler())
        log.addHandler(logging.StreamHandler())

        log.setLevel(logging.INFO)
        log.info("romi start")

        connection_error_printed = False
        cont = True
        while cont:
            try:
                robot.play_welcome_message()
                connection_error_printed = False
                log.info("Connected to Romi board")

                while True:
                    (buttonA, buttonB, buttonC) = robot.read_buttons()
                    if buttonB and buttonC:
                        log.info("Stopping raspberry")
                        robot.play_goodbye_message()
                        os.system("sudo halt")
                        cont = False
                    if buttonA and buttonB:
                        log.info("Restarting raspberry")
                        robot.play_goodbye_message()
                        os.system("sudo reboot")
                        cont = False
                    if buttonA:
                        if robot_wii_controler is None:
                            log.info("Creating RobotWiiControler")
                            robot_wii_controler = RobotWiiControler(robot)
                        else:
                            log.info("Releasing RobotWiiControler")
                            robot_wii_controler.release()
                            robot_wii_controler = None

                    sleep(1)
            except IOError as e:
                if not connection_error_printed:
                    log.info("Cannot connect to Romi board")
                    connection_error_printed = True
                sleep(10)

    except KeyboardInterrupt as e:
        logging.info("Stopped")

    except Exception as e:
        logging.error("Error happened")
        logging.error(e)

    finally:
        if robot_wii_controler is not None:
            robot_wii_controler.release()
            logging.info("Releasing robot wii controler")

        logging.info("Stopping robot")
        robot.stop()


if __name__ == "__main__":
    main()
