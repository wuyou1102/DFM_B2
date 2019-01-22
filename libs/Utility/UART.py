# -*- encoding:UTF-8 -*-
from Serial import Serial
import logging
from libs.Config.ErrorCode import ErrorCode
import Alert
from libs.Command import AT as command
import time
from libs.Utility import convert_freq_point

logger = logging.getLogger(__name__)

timeout = 5


class UART(Serial):
    def __init__(self, port):
        Serial.__init__(self, port=port)
        self.__serial_number = None

    @property
    def SerialNumber(self):
        return self.__serial_number

    def get_serial_number(self):
        cmd = command.get_serial_number()
        return self._get(cmd=cmd)

    def set_serial_number(self, serial):
        cmd = command.set_serial_number(value=serial)
        if self.__set(cmd=cmd):
            output = self.get_serial_number()
            if output == serial:
                self.__serial_number = output
                return True
            return False
        return False

    def get_flag_result(self, flag):
        cmd = command.get_flag_result(flag=flag)
        result = self._get(cmd=cmd)
        time.sleep(0.025)
        return result

    def set_flag_result(self, flag, result):
        cmd = command.set_flag_result(flag=flag, result=result)
        return self._set(cmd=cmd)

    def is_uart_connected(self):
        serial = self._get(cmd=command.get_serial_number())
        if serial:
            self.__serial_number = serial
            return True
        if self._get(cmd=command.is_button_clicked()) in ["True", "False"]:
            self.__serial_number = ""
            return True
        return False

    def is_usb_connected(self):
        cmd = command.is_usb_connected()
        if self._get(cmd=cmd) == "True":
            return True
        return False

    def reset_button_click(self):
        cmd = command.reset_button_click()
        return self._set(cmd=cmd)

    def is_button_clicked(self):
        cmd = command.is_button_clicked()
        if self._get(cmd=cmd) == "True":
            return True
        return False

    # 协议栈接口
    def set_radio_frequency_power(self, value):
        cmd = command.set_radio_frequency_power(value=value)
        return self._protocol_set(cmd=cmd)

    def get_radio_frequency_power(self):
        cmd = command.get_radio_frequency_power()
        try:
            result = self._protocol_get(cmd=cmd)
            result = int(result, 16)
            return result
        except ValueError:
            return self.get_radio_frequency_power()

    def set_register(self, address, value):
        cmd = command.set_register(address=address, value=value)
        return self._protocol_set(cmd=cmd)

    def get_register(self, address):
        cmd = command.get_register(address=address)
        return self._protocol_get(cmd=cmd)

    def set_frequency_point(self, value):
        cmd = command.set_frequency_point(value=value)
        return self._protocol_set(cmd=cmd)

    def get_frequency_point(self):
        cmd = command.get_frequency_point()
        try:
            result = self._protocol_get(cmd=cmd)
            result = convert_freq_point(result)
            return result
        except ValueError:
            return self.get_frequency_point()

    def hold_baseband(self):
        cmd = command.hold_baseband()
        result = self._protocol_set(cmd=cmd)
        time.sleep(0.5)
        return result

    def release_baseband(self):
        cmd = command.release_baseband()
        result = self._protocol_set(cmd=cmd)
        time.sleep(0.5)
        return result

    def set_qam(self, value):
        cmd = command.set_qam(value=value)
        return self._protocol_set(cmd=cmd)

    def get_qam(self):
        cmd = command.get_qam()
        return self._protocol_get(cmd=cmd)

    def get_br_bler(self):
        cmd = command.get_br_bler()
        return self._protocol_get(cmd=cmd)

    def get_slot_bler(self):
        cmd = command.get_slot_bler()
        return self._protocol_get(cmd=cmd)

    def set_tx_mode_20m(self):
        cmd = command.set_tx_mode_20m()
        return self._protocol_set(cmd=cmd)

    def set_rx_mode_20m(self):
        cmd = command.set_rx_mode_20m()
        return self._protocol_set(cmd=cmd)

    def is_instrument_connected(self):
        cmd = command.is_instrument_connected()
        output = self._protocol_get(cmd=cmd)
        if output == "0x1":
            return True
        return False

    def _protocol_get(self, cmd):
        output = self._get(cmd=cmd)
        if output is None:
            Alert.Error("串口通信失败，请重试")
            raise RuntimeError
        return output

    def _protocol_set(self, cmd):
        output = self._get(cmd=cmd)
        if output is None:
            Alert.Error("串口通信失败，请重试")
            raise RuntimeError
        if output == "0x0":
            return True
        return False

    def _get(self, cmd, sleep=0.02):
        result = self.execute_command(command=cmd, sleep=sleep)
        if result.exit_code == 0:
            return result.outputs
        elif result.exit_code == ErrorCode.SERIAL_EXCEPTION:
            Alert.Error("sssssss")
            return None
        elif result.exit_code == ErrorCode.WRONG_TERMINATOR:
            for x in range(2, 5):
                result = self.execute_command(command=cmd, sleep=sleep + 0.01 * x)
                if result.exit_code == 0:
                    return result.outputs
            return None
        elif result.exit_code == ErrorCode.TIMING_ERROR:
            self.send(command="", sleep=0.008)
            # Alert.Error("111")
            for x in range(2, 5):
                result = self.execute_command(command=cmd, sleep=sleep + 0.01 * x)
                if result.exit_code == 0:
                    return result.outputs
        else:
            raise KeyError("Unknow exit code: \"%s\"" % repr(result.exit_code))

    def _set(self, cmd, sleep=0.02):
        for x in range(3):
            if self.__set(cmd=cmd, sleep=sleep):
                return True
        Alert.Error(u"设置失败")
        return False

    def __set(self, cmd, sleep=0.01):
        result = self.execute_command(command=cmd, sleep=sleep)
        if result.exit_code == 0:
            if result.outputs == "True":
                return True
            return False
        elif result.exit_code == ErrorCode.SERIAL_EXCEPTION:
            Alert.Error(u"串口通信失败，请重启串口后重试。")
            return False
        elif result.exit_code == ErrorCode.WRONG_TERMINATOR:
            for x in range(2, 5):
                result = self.execute_command(command=cmd, sleep=sleep + 0.01 * x)
                if result.exit_code == 0:
                    if result.outputs == "True":
                        return True
                    return False
            return False
        else:
            raise KeyError("Unknow exit code: \"%s\"" % repr(result.exit_code))
