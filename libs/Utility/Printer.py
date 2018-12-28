# -*- encoding:UTF-8 -*-
import logging
import traceback
import time

logger = logging.getLogger(__name__)


def get_timestamp(time_fmt='%Y_%m_%d-%H_%M_%S', t=None):
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


class TestPrint(object):
    def __init__(self):
        self.__redirect = ''
        self.__log_path = ''
        self.__logs = list()

    def __print(self, msg):
        self.__logs.append(msg)
        if self.__redirect:
            self.__redirect(msg)
        else:
            logger.info(msg=msg)

    def __write(self, msg):
        if self.__log_path:
            with open(self.__log_path, 'a', 1) as log:
                log.write(msg + '\n')

    def __format_msg(self, msg):
        return msg.strip('\r\n')

    def info(self, msg):
        msg = "{timestamp}  {level}: {msg}".format(timestamp=get_timestamp(), level="INFO",
                                                   msg=self.__format_msg(msg=msg))
        self.__print(msg)
        self.__write(msg)

    def warm(self, msg):
        msg = "{timestamp}  {level}: {msg}".format(timestamp=get_timestamp(), level="WARM",
                                                   msg=self.__format_msg(msg=msg))
        self.__print(msg)
        self.__write(msg)

    def error(self, msg):
        msg = "{timestamp} {level}: {msg}".format(timestamp=get_timestamp(), level="ERROR",
                                                  msg=self.__format_msg(msg=msg))
        self.__print(msg)
        self.__write(msg)

    def debug(self, msg):
        msg = "{timestamp} {level}: {msg}".format(timestamp=get_timestamp(), level="DEBUG",
                                                  msg=self.__format_msg(msg=msg))
        self.__print(msg)
        self.__write(msg)

    def result(self, msg):
        msg = "{timestamp}  {level}: {msg}".format(timestamp=get_timestamp(), level="RSLT",
                                                   msg=self.__format_msg(msg=msg))
        self.__print(msg)
        self.__write(msg)

    def traceback(self):
        self.error('Exception')
        tmp = traceback.format_exc()
        if tmp != 'None\n':
            self.error(tmp.strip('\n'))

    def set_redirect(self, redirect):
        self.__redirect = redirect
        if redirect is not None:
            for line in self.__logs:
                self.__redirect(line)

    def set_log_path(self, path):
        self.__log_path = path
