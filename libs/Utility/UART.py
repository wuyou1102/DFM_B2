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

INTERVAL_TIME = 0.016
MAX_RETRY_COUNT = 3


class UART(Serial):
    def __init__(self, port):
        Serial.__init__(self, port=port)
        self.__serial_number = None

    @property
    def SerialNumber(self):
        return self.__serial_number

    def get_serial_number(self):
        cmd = command.get_serial_number()
        self.__serial_number = self._get(cmd=cmd)
        return self.__serial_number

    def set_serial_number(self, serial):
        cmd = command.set_serial_number(value=serial)
        return self._set(cmd=cmd)

    def get_all_flag_results(self):
        cmd = command.get_all_flag_result()
        result = self._get(cmd)
        if len(result) == 32:
            return result
        return None

    def get_flag_result(self, flag):
        cmd = command.get_flag_result(flag=flag)
        result = self._get(cmd=cmd)
        for x in ["False", "True", "NotTest"]:
            if result.endswith(x):
                return x
        return "NotTest"

    def set_flag_result(self, flag, result):
        cmd = command.set_flag_result(flag=flag, result=result)
        return self._set(cmd=cmd)

    def is_uart_connected(self):
        cmd = command.is_button_clicked()
        result = self._get(cmd=cmd)
        if result is not None:
            for x in ["True", "False"]:
                if result.endswith(x):
                    return True
        return False

    def is_usb_connected(self):
        cmd = command.is_usb_connected()
        if self._get(cmd=cmd).endswith("True"):
            return True
        return False

    def reset_button_click(self):
        cmd = command.reset_button_click()
        return self._set(cmd=cmd)

    def is_button_clicked(self):
        cmd = command.is_button_clicked()
        if self._get(cmd=cmd).endswith("True"):
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
        if output.endswith("0x1"):
            return True
        return False

    def _protocol_get(self, cmd, retry=True):
        return self._get(cmd=cmd, retry=retry)

    def _protocol_set(self, cmd, retry=True):
        result = self.__execute_command(cmd=cmd, retry=retry)
        if result.exit_code == 0:
            if result.outputs.endswith("0x0"):
                return True
            else:
                Alert.Error(u"设置失败")
                return False
        else:
            Alert.Error(result.outputs)
            return False

    def _get(self, cmd, retry=True):
        result = self.__execute_command(cmd=cmd, retry=retry)
        if result.exit_code == 0:
            return result.outputs
        else:
            Alert.Error(result.outputs)
            return None

    def _set(self, cmd, retry=True):
        result = self.__execute_command(cmd=cmd, retry=retry)
        if result.exit_code == 0:
            if result.outputs.endswith("True"):
                return True
            else:
                Alert.Error(u"设置失败")
                return False
        else:
            Alert.Error(result.outputs)
            return False

    def __execute_command(self, cmd, count=0, retry=True):
        result = self.execute_command(command=cmd, sleep=INTERVAL_TIME)
        if result.exit_code == 0:
            return result
        elif result.exit_code == ErrorCode.SERIAL_EXCEPTION:
            return result
        elif result.exit_code == ErrorCode.WRONG_TERMINATOR:
            if count < MAX_RETRY_COUNT and retry:
                self.flush()
                return self.__execute_command(cmd=cmd, count=count + 1)
            return result
        elif result.exit_code == ErrorCode.EMPTY_OUTPUT_EXCEPTION:
            cmd = " " * 50 + cmd
            if count < MAX_RETRY_COUNT and retry:
                self.flush()
                return self.__execute_command(cmd=cmd, retry=False)
            return result
        else:
            raise KeyError("Unknown exit code: \"%s\"" % repr(result.exit_code))
