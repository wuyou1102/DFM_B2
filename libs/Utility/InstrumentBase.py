# -*- encoding:UTF-8 -*-
from libs.Utility import Logger
import pyvisa
import logging
import threading
import time

logger = logging.getLogger(__name__)

ResourceManager = pyvisa.ResourceManager()


class SCPI(object):
    def __init__(self, port, timeout=2000):
        self.__port = port
        self.__timeout = timeout
        self.__session = self.__init_session()
        self.__lock = threading.Lock()
        self.model_name = self.__get_model_name()

    def __init_session(self):

        session = ResourceManager.open_resource(self.__port)
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


if __name__ == '__main__':
    resources = ResourceManager.list_resources()
    print resources
    for resource in resources:
        inst = SCPI(resource)
        if inst.model_name == 'N9020A':
            # print '======================================================================================='
            # inst.send_command("CONF:BPOW")
            #
            # inst.send_command("DISP:TXP:VIEW:WIND:TRAC:Y:RLEV 40dBm")
            # inst.send_command("CORR:SA:GAIN -20.2")
            # inst.send_command("FREQ:CENT 2410MHz")
            # inst.send_command("TXP:METH THR")
            # inst.send_command("TXP:THR -15")
            # inst.send_command("TRIG:TXP:SOUR IMM")
            # inst.send_command("TXP:BAND 20000kHz")
            for x in range(10):
                time.sleep(1)
                print inst.send_command("FETC:BPOW?")

        inst.disconnect()

        # inst.send_command("CONF:BPOW")

        # x信号发生器
        # for x in range(2410,2450):
        #     inst.send_command(command="FREQ %s MHz" % x)
        #     time.sleep(1)
        # inst.send_command(command=":POWer:LEVel -32.1DBM")
        # inst.send_command(command=":FREQuency:FIXed 2.51GHZ")
        # inst.send_command('RADio:ARB:SCLock:RATE 22900kHz')
        #       inst.send_command('RADio:ARB:SCLock:RATE?')
        # inst.send_command(":RAD:ARB ON")
        # inst.send_command(":RAD:ARB?")
        # inst.send_command(":POWer:ALC OFF")
        # inst.send_command(":POWer:ALC?")
        # SR_SLOT_20M_16QAM_12_1P25X4_1T
        # inst.send_command(':SOURce:RADio:ARB:WAVeform "WFM1:SR_SLOT_20M_16QAM_12_1P25X4_1T.DAT"')
