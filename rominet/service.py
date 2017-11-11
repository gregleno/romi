#!/usr/bin/env python

import logging
import os
from threading import Thread
from time import sleep
from robot import Robot
from robot_wii_controler import RobotWiiController
from webserver import run_web_server


def main():
    rob = Robot()

    thread = Thread(target=control_loop, args=[rob])
    thread.setDaemon(True)
    thread.start()

    run_web_server(rob)


def control_loop(rob):
    robot_wii_controller = None
    robot = rob

    try:
        log = logging.getLogger('romi')
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
                        robot.stop()
                        os.system("sudo halt")
                        cont = False
                        break
                    if buttonA and buttonB:
                        log.info("Restarting raspberry")
                        robot.play_goodbye_message()
                        robot.stop()
                        os.system("sudo reboot")
                        cont = False
                        break
                    if buttonA:
                        if robot_wii_controller is None:
                            log.info("Creating RobotWiiControler")
                            robot_wii_controller = RobotWiiController(robot)
                        else:
                            log.info("Releasing RobotWiiControler")
                            robot_wii_controller.release()
                            robot_wii_controller = None

                    sleep(1)
            except IOError:
                if not connection_error_printed:
                    log.info("Cannot connect to Romi board")
                    connection_error_printed = True
                sleep(10)

    except KeyboardInterrupt:
        logging.info("Stopped by KeyboardInterrupt")

    except Exception as e:
        logging.error("Error happened")
        logging.error(e)

    finally:
        if robot_wii_controller is not None:
            robot_wii_controller.release()
            logging.info("Releasing robot wii controller")

        logging.info("Stopping robot")
        robot.stop()


if __name__ == "__main__":
    main()
