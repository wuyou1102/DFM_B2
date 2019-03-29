# -*- encoding:UTF-8 -*-
import pyvisa
import logging
import threading
import time

logger = logging.getLogger(__name__)


class SCPI(object):
    def __init__(self, port, timeout=2000):
        self.__port = port
        self.__timeout = timeout
        self.__session = self.__init_session()
        self.__lock = threading.Lock()
        self.model_name = self.__get_model_name()

    def __init_session(self):
        rm = pyvisa.ResourceManager()
        session = rm.open_resource(self.__port)
        session.timeout = self.__timeout
        return session

    def __get_model_name(self):
        model_info = self.send_command('*IDN?')
        return model_info.split(',')[1]

    def disconnect(self):
        if self.__session:
            self.__session.close()

    def __query(self, cmd):
        logger.debug("SCPI|Query  :%s" % cmd)
        return self.__session.query(cmd).strip('\r\n')

    def __write(self, cmd):
        logger.debug("SCPI|Write  :%s" % cmd)
        return self.__session.write(cmd)[1]

    def send_command(self, command):
        if self.__lock.acquire():
            try:
                output = self.__query(command) if command.endswith('?') else self.__write(command)
                logger.debug("SCPI|Result :%s" % str(output))
                return output
            finally:
                time.sleep(0.05)
                self.__lock.release()


class SharedBaseInstrument(object):
    pool = dict()

    @classmethod
    def create(cls):
        raise NotImplementedError

    @classmethod
    def get_instruments(cls):
        return cls.pool.keys()


if __name__ == '__main__':
    a = SCPI('sss')
    a.send_command('ssss')
