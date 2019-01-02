# -*- encoding:UTF-8 -*-
from Serial import Serial
import random
import logging
import Timeout

logger = logging.getLogger(__name__)

timeout = 5


class UART(Serial):
    def __init__(self, port):
        Serial.__init__(self, port=port)
        self.__serial_number = self.__get_serial_number()

    def get_serial_number(self):
        return self.__serial_number

    @Timeout.timeout(timeout)
    def __get_serial_number(self):
        if self.lock.acquire():
            try:
                self.send_command("get_serial_number")
                line = random.choice(["", "abcdefghijklmnopqrstuvwxyz"])
                logger.debug("get_serial_number:\"%s\"" % line)
                return line
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    @Timeout.timeout(timeout)
    def set_serial_number(self, serial="abcdefghijklmnopqrstuvwxyz"):
        if self.lock.acquire():
            try:
                self.send_command("set_serial_number %s" % serial)
                line = random.choice(["True", "False"])
                logger.debug("set_serial_number:\"%s\"" % line)
                if line == "True":
                    self.__serial_number = serial
                    return True
                return False
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    @Timeout.timeout(timeout)
    def get_flag_result(self, flag):
        if self.lock.acquire():
            try:
                self.send_command("get_flag_result %s" % flag)
                line = random.choice(["Pass", "Fail", "NotTest"])
                logger.debug("get_flag_result[%s]:\"%s\"" % (flag, line))
                return line
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    def set_flag_result(self, flag, result):
        print flag, result

    def read_reg(self, address):
        pass

    def write_reg(self, address, value):
        pass

    def import_reg(self, file):
        pass

    def is_connect(self):
        return True
