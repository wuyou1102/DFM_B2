# -*- encoding:UTF-8 -*-
import serial
import logging
import serial.tools.list_ports
import threading
import re

Logger = logging.getLogger(__name__)
port_pattern = re.compile(r'(COM\d+)')


class Serial(object):
    def __init__(self, port, baudrate=115200):
        Logger.debug('Serial| Init port.')
        self.lock = threading.Lock()
        baudrate = baudrate if baudrate in [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200,
                                            230400, 380400, 460800, 921600] else 115200
        self.port = self.__convert_port(port=port)
        self.__session = serial.Serial(port=self.port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=2)

    def __convert_port(self, port):
        return re.findall(port_pattern, port)[0]

    def get_port(self):
        return self.port

    def read_line(self):
        data = ''
        while self.is_open():
            try:
                s = self.__session.read()
            except TypeError:
                continue
            except serial.serialwin32.SerialException:
                continue
            except AttributeError:
                continue
            data += s
            if data.endswith('\r') or data.endswith('\n'):
                data = data.strip('\r\n')
                if data:
                    return data
        return data

    def send_command(self, cmd):
        cmd = cmd.strip('\r\n') + '\r'
        Logger.debug('Serial| Send Command: %s ' % cmd)
        if self.is_open():
            Logger.debug('Serial| Port is already open.')
            self.__session.write(cmd.encode())

    def is_open(self):
        return self.__session.is_open

    def close(self):
        if self.is_open():
            self.__session.close()
        return True

    @staticmethod
    def get_ports():
        ports = list()
        port_list = serial.tools.list_ports.comports()
        if len(port_list) == 0:
            Logger.info(u'Can not find ports.')
            return ports
        else:
            for port in list(port_list):
                port_name = port[1]
                ports.append(port_name)
            return sorted(ports, reverse=True)
