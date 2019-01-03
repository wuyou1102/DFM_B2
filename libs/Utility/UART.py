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
                line = random.choice(list('abcdefghijklmnopqrstuvwxyz'))
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
                self.send_command(u"set_serial_number %s" % serial)
                line = random.choice(["True", "False"])
                if line == "True":
                    logger.debug("Set Serial Number: \"Success\"")
                    self.__serial_number = serial
                    return True
                logger.error("Set Serial Number: \"Failure\"")
                return False
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    @Timeout.timeout(timeout)
    def get_flag_result(self, flag):
        if self.lock.acquire():
            try:
                cmd = "get_flag_result {flag}".format(flag=flag)
                self.send_command(cmd)
                line = random.choice(["Pass", "Fail", "NotTest"])
                logger.debug("Get <%s> Flag Result :\"%s\"" % (flag, line))
                return line
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    def set_flag_result(self, flag, result):
        if self.lock.acquire():
            try:
                cmd = "set_flag_result {flag} {result}".format(flag=flag, result=result)
                self.send_command(cmd)
                line = random.choice(["True", "False"])
                if line == "True":
                    logger.debug("Set <%s> Flag Result :\"Success\"")
                    return True
                logger.error("Set <%s> Flag Result :\"Failure\"")
                return False
            except Timeout.Timeout():
                return False
            finally:
                self.lock.release()

    def read_reg(self, address):
        pass

    def write_reg(self, address, value):
        pass

    def import_reg(self, file):
        pass

    def is_connect(self):
        return True

    def reset_button_click(self):
        return True

    def get_button_click(self):
        return random.choice([False,False,False,False,False,False,True])
