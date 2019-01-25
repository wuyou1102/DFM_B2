# -*- encoding:UTF-8 -*-
import serial
import logging
import serial.tools.list_ports
import threading
import Timeout
import time
from libs.Utility import ExecuteResult

from libs.Config.ErrorCode import ErrorCode

Logger = logging.getLogger(__name__)


class Serial(object):
    def __init__(self, port, baudrate=921600):
        Logger.debug('Serial| Init port.')
        self.lock = threading.Lock()
        baudrate = baudrate if baudrate in [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200,
                                            230400, 380400, 460800, 921600] else 115200
        self.__session = serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=2)

    def execute_command(self, command, sleep):
        Logger.debug('********************************************************')
        Logger.debug('* UART COMMAND:\"%s\"' % command)
        if self.lock.acquire():
            try:
                self.send(command=command, sleep=sleep)
                result = self.read()
                Logger.debug("* STDOUT: {result}".format(result=repr(result)))
                if result.endswith('\n'):
                    return ExecuteResult(exit_code=0, outputs=result.strip('\n'))
                else:
                    return ExecuteResult(exit_code=ErrorCode.WRONG_TERMINATOR, outputs=ErrorCode.WRONG_TERMINATOR.MSG)
            except serial.SerialException:
                return ExecuteResult(exit_code=ErrorCode.SERIAL_EXCEPTION, outputs=ErrorCode.SERIAL_EXCEPTION.MSG)
            finally:
                Logger.debug('********************************************************')
                self.lock.release()

    def send(self, command, sleep):
        command = command.strip('\r\n') + '\n'
        self.__session.write(command.encode())
        time.sleep(sleep)

    def read(self):
        return self.__session.read_all()

    def flush(self):
        self.send("", sleep=0.016)
        self.__session.flushInput()
        self.__session.flushOutput()

    @Timeout.timeout(5)
    def read_line(self):
        data = ''
        while self.is_open():
            s = self.__session.read()
            data += s
            Logger.info(repr(s))
            if data.endswith('\n'):
                data = data.strip('\r\n')
                break
        Logger.debug('Serial| Get Output: %s ' % data)
        return data

    @Timeout.timeout(5)
    def read_until(self):
        return self.__session.read_until()

    def send_command(self, cmd):
        Logger.debug('Serial| Send Command: %s ' % cmd)
        cmd = cmd + '\n'
        if self.is_open():
            self.__session.write(cmd.encode())
            time.sleep(0.01)

    def is_open(self):
        return self.__session.is_open

    def close(self):
        if self.is_open():
            self.__session.close()
        return True

    @staticmethod
    def list_ports():
        ports = list()
        port_list = serial.tools.list_ports.comports()
        if len(port_list) == 0:
            Logger.info(u'Can not find ports.')
            return ports
        else:
            for port in list(port_list):
                port_name = port[0]
                ports.append(port_name)
            return sorted(ports, reverse=False)
