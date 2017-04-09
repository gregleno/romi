#!/usr/bin/env python3

import logging
from systemd.journal import JournalHandler
import time
from time import sleep
from a_star import AStar
import os


def play_welcome_message():
    pattern = ((1, 0, 0),
               (0, 1, 0),
               (0, 0, 1),
               (1, 0, 0),
               (0, 1, 0),
               (0, 0, 1),
               (0, 0, 0),
               (1, 1, 1),
               (0, 0, 0),
               (1, 1, 1),
               (0, 0, 0),
               )
    for leds in pattern:
        a_star.leds(*leds)
        sleep(0.5)


try:
    a_star = AStar()
    log = logging.getLogger('romi')
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)
    log.info("romi start")

    connection_error_printed = False
    while True:
        try:
            play_welcome_message()
            connection_error_printed = False
            log.info("Connected to Romi board")

            while True:
                (buttonA, buttonB, buttonC) = a_star.read_buttons()
                if buttonB and buttonC:
                    log.info("Stopping raspberry")
                    os.system("sudo halt")
                if buttonA and buttonB:
                    log.info("Restarting raspberry")
                    os.system("sudo reboot")
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
