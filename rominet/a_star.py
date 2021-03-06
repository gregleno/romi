# Copyright Pololu Corporation.  For more information, see https://www.pololu.com/
import struct
import time
import logging
from multiprocessing import Lock

try:
    import smbus
except ImportError:
    smbus = None


bus_lock = Lock()


class AStar(object):

    def __init__(self):
        self.bus = smbus.SMBus(1)

    def read_unpack(self, address, size, format):
        # Ideally we could do this:
        #    byte_list = self.bus.read_i2c_block_data(20, address, size)
        # But the AVR's TWI module can't handle a quick write->read transition,
        # since the STOP interrupt will occasionally happen after the START
        # condition, and the TWI module is disabled until the interrupt can
        # be processed.
        #
        # A delay of 0.0001 (100 us) after each write is enough to account
        # for the worst-case situation in our example code.
        byte_list = []
        with bus_lock:
            try:
                self.bus.write_byte(20, address)
                time.sleep(0.0001)
                for n in range(0, size):
                    byte_list.append(self.bus.read_byte(20))
            except IOError:
                logging.exception("IOError in read_unpack")
                for n in range(0, size):
                    byte_list.append(0)
                time.sleep(0.0001)

        return struct.unpack(format, bytes(bytearray(byte_list)))

    def write_pack(self, address, format, *data):
        data_array = map(ord, list(struct.pack(format, *data)))
        with bus_lock:
            try:
                self.bus.write_i2c_block_data(20, address, data_array)
            except IOError:
                logging.exception("IOError in write_pack")
            finally:
                time.sleep(0.0001)

    def leds(self, red, yellow, green):
        self.write_pack(0, 'BBB', yellow, green, red)

    def play_notes(self, notes):
        self.write_pack(24, 'B15s', 1, notes.encode("ascii"))

    def motors(self, left, right):
        self.write_pack(6, 'hh', left, right)

    def read_buttons(self):
        return self.read_unpack(3, 3, "???")

    def read_battery_millivolts(self):
        return self.read_unpack(10, 2, "H")

    def read_analog(self):
        return self.read_unpack(12, 12, "HHHHHH")

    def read_encoders(self):
        return self.read_unpack(39, 4, 'hh')

    def test_read8(self):
        self.read_unpack(0, 8, 'cccccccc')

    def test_write8(self):
        self.bus.write_i2c_block_data(20, 0, [0, 0, 0, 0, 0, 0, 0, 0])
        time.sleep(0.0001)
