# -*- encoding:UTF-8 -*-
import socket
import logging
import threading
import time
from libs.Utility import ExecuteResult
from libs.Config.ErrorCode import ErrorCode
from libs.Command import AT as command
import Alert
from libs.Utility import convert_freq_point

Logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, address="192.168.1.1", port=51341):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)
        self._address = address
        self._port = port
        self.__serial_number = ""
        self.__lock = threading.Lock()
        self._connect(address, port)

    def _connect(self, address, port):
        self._socket.connect((address, port))

    def reconnect(self):
        temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp.settimeout(1)
        for i in range(1, 11):
            try:
                temp.connect((self._address, self._port))
                self._socket = temp
                return True
            except socket.timeout:
                pass
            except socket.error:
                pass
        Logger.error("Socket Reconnect Fail")
        return False

    @property
    def SerialNumber(self):
        return self.__serial_number

    def reboot(self):
        cmd = command.reboot()
        Logger.info('********************************************************')
        Logger.info('* SOCKET COMMAND:\"%s\"' % cmd)
        if self.__lock.acquire():
            try:
                self.send(command=cmd)
                return True
            except socket.error:
                return False
            finally:
                Logger.info('********************************************************')
                self.__lock.release()

    def get_serial_number(self):
        cmd = command.get_serial_number()
        self.__serial_number = self._get(cmd=cmd)
        return self.__serial_number

    def load_protocol_stack(self):
        cmd = command.load_protocol_stack()
        return self._set(cmd=cmd)

    def unload_protocol_stack(self):
        cmd = command.unload_protocol_stack()
        return self._set(cmd=cmd)

    def set_serial_number(self, serial):
        cmd = command.set_serial_number(value=serial)
        return self._set(cmd=cmd)

    def get_all_flag_results(self):
        cmd = command.get_all_flag_result()
        result = self._get(cmd)
        if result is None:
            return None
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

    def start_web_server(self):
        cmd = command.start_web_server()
        return self._set(cmd=cmd)

    def stop_web_server(self):
        cmd = command.stop_web_server()
        return self._set(cmd=cmd)

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

    def get_rssi(self, idx):
        cmd = command.get_rssi(idx=idx)
        return self._protocol_get(cmd=cmd)

    def get_rssi_and_bler(self):
        cmd = command.get_rssi_bler()
        return self._protocol_get(cmd)

    def set_tx_mode_20m(self):
        cmd = command.set_tx_mode_20m()
        return self._protocol_set(cmd=cmd)

    def set_rx_mode_20m(self):
        cmd = command.set_rx_mode_20m()
        return self._protocol_set(cmd=cmd)

    def set_signal_0(self, ON=True):
        value = '1' if ON else '0'
        cmd = command.set_signal_0(value)
        return self._protocol_set(cmd=cmd)

    def set_signal_1(self, ON=True):
        value = '1' if ON else '0'
        cmd = command.set_signal_1(value)
        return self._protocol_set(cmd=cmd)

    def is_signal_opened(self, idx):
        cmd = command.get_signal_status(idx)
        output = self._protocol_get(cmd=cmd)
        if output is not None:
            try:
                is_opened = int(output)
                if is_opened == 1:
                    return True
            except ValueError:
                Logger.error("Get an abnormal value: \"%s\"" % repr(output))
        return False

    def is_instrument_connected(self):
        cmd = command.is_instrument_connected()
        output = self._protocol_get(cmd=cmd)
        if output is not None:
            try:
                is_connected = int(output)
                if is_connected == 1:
                    return True
            except ValueError:
                Logger.error("Get an abnormal value: \"%s\"" % repr(output))
        return False

    def _protocol_get(self, cmd):
        for i in range(3):
            try:
                result = self.execute_command(command=cmd)
                if result.exit_code == 0 and len(result.outputs) == 16:
                    return result.outputs
            except ValueError and TypeError:
                Logger.error("[%s]Get an abnormal value: \"%s\"" % (i, repr(result.outputs)))
        Alert.Error(result.outputs)
        return None

    def _protocol_set(self, cmd):
        for i in range(3):
            try:
                result = self.execute_command(command=cmd)
                if result.exit_code == 0:
                    if len(result.outputs) == 16 and int(result.outputs) == 0:
                        return True
            except ValueError and TypeError:
                Logger.error("[%s]Get an abnormal value: \"%s\"" % (i, repr(result.outputs)))
        Alert.Error(u"设置失败")
        return False

    def _get(self, cmd):
        for i in range(3):
            result = self.execute_command(command=cmd)
            if result.exit_code == 0:
                return result.outputs
        Alert.Error(result.outputs)
        return None

    def _set(self, cmd):
        for i in range(3):
            result = self.execute_command(command=cmd)
            if result.exit_code == 0:
                if result.outputs.endswith("True"):
                    return True
        Alert.Error(u"设置失败")
        return False

    def execute_command(self, command, sleep=0.015):
        Logger.info('********************************************************')
        Logger.info('* SOCKET COMMAND:\"%s\"' % command)
        if self.__lock.acquire():
            try:
                self.send(command=command)
                time.sleep(sleep)
                result = self.read()
                Logger.info("* STDOUT: {result}".format(result=repr(result)))
                if result.endswith('\n'):
                    return ExecuteResult(exit_code=0, outputs=result.strip('\n'))
                else:
                    return ExecuteResult(exit_code=ErrorCode.WRONG_TERMINATOR,
                                         outputs=u"执行命令:%s\n" % command + ErrorCode.WRONG_TERMINATOR.MSG)
            except socket.error:
                return ExecuteResult(exit_code=ErrorCode.SOCKET_EXCEPTION,
                                     outputs=u"执行命令:%s\n" % command + ErrorCode.SOCKET_EXCEPTION.MSG)
            finally:
                Logger.info('********************************************************')
                time.sleep(sleep)
                self.__lock.release()

    def send(self, command):
        command = command.strip('\r\n') + '\n'
        self._socket.sendall(command)

    def read(self, buffersize=1024):
        return self._socket.recv(buffersize)

    def close(self):
        return self._socket.close()


if __name__ == '__main__':
    s = Client(address='192.168.1.1')
    for x in range(1,33):
        s.set_flag_result(x, 2)
