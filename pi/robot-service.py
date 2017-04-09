#!/usr/bin/env python

import logging
from systemd.journal import JournalHandler
import time
from time import sleep
from a_star import AStar
from wiiremote import WiiRemote
import os

NO_LED = (0, 0, 0)
ALL_LEDS = (1, 1, 1)
LED1 = (1, 0, 0)
LED2 = (0, 1, 0)
LED3 = (0, 0, 1)


def play_welcome_message():
    pattern = (LED1, LED2, LED3, LED1, LED2, LED3, NO_LED, ALL_LEDS, NO_LED, ALL_LEDS, NO_LED)
    for leds in pattern:
        a_star.leds(*leds)
        sleep(0.2)


def play_goodbye_message():
    pattern = (ALL_LEDS, (1, 1, 0), (1, 0, 0), NO_LED)
    for leds in pattern:
        a_star.leds(*leds)
        sleep(0.4)

try:
    a_star = AStar()
    log = logging.getLogger('romi')
    log.addHandler(JournalHandler())
    ch = logging.StreamHandler()
    log.addHandler(ch)

    log.setLevel(logging.INFO)
    log.info("romi start")

    connection_error_printed = False
    wiimote = None
    cont = True
    while cont:
        try:
            play_welcome_message()
            connection_error_printed = False
            log.info("Connected to Romi board")

            while True:
                (buttonA, buttonB, buttonC) = a_star.read_buttons()
                if buttonB and buttonC:
                    log.info("Stopping raspberry")
                    play_goodbye_message()
                    os.system("sudo halt")
                    cont = False
                if buttonA and buttonB:
                    log.info("Restarting raspberry")
                    play_goodbye_message()
                    os.system("sudo reboot")
                    cont = False
                if buttonA:
                    if wiimote is not None:
                        log.info("Releasing wiimote")
                        wiimote.release()
                        wiimote = None
                    else:
                        log.info("Connecting to wiimote")
                        pattern = (ALL_LEDS, NO_LED, ALL_LEDS, NO_LED, ALL_LEDS, NO_LED)
                        for leds in pattern:
                            a_star.leds(*leds)
                            sleep(0.1)
                        wiimote = WiiRemote.connect()
                        if wiimote is not None:
                            log.info("Connected to wiimote")

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
