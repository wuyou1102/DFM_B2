# -*- encoding:UTF-8 -*-
__HEAD = "AT+DFM="


def get_gain_and_power():  # 获取当前中心增益和功率
    cmd = "read_refgain_targetpwr"
    return __HEAD + cmd


def set_gain_and_power(gain, power):  # 设置当前中心增益和功率
    cmd = "set_refgain_targetpwr,{gain},{power}".format(gain=gain, power=power)
    return __HEAD + cmd


def get_rssi(idx):
    cmd = "read_0{idx}_rssi".format(idx=idx)
    return __HEAD + cmd


def get_rssi_bler():
    cmd = "read_rssi_bler"
    return __HEAD + cmd


def enable_spi(enable=True):
    enable = 1 if enable is True else 0
    cmd = "set_spi_en,{enable}".format(enable=enable)
    return __HEAD + cmd


def enable_tssi_2g(enable=True):
    enable = 1 if enable is True else 0
    cmd = "set_tssi_2g_en,{enable}".format(enable=enable)
    return __HEAD + cmd


def enable_tssi_5g(enable=True):
    enable = 1 if enable is True else 0
    cmd = "set_tssi_5g_en,{enable}".format(enable=enable)
    return __HEAD + cmd


def set_radio_frequency_power(value):
    if type(value) != int:
        raise TypeError("Frequency Power must <type 'int'>, but now is \"%s\"" % type(value))
    if value not in range(32):
        raise ValueError("Frequency Power must in range (0x00- 0x1F), but now is \"%s\"" % value)
    cmd = "set_rf_pwr,{value}".format(value=hex(value))
    return __HEAD + cmd


def get_radio_frequency_power():
    cmd = "read_rf_pwr"
    return __HEAD + cmd


def set_register(address, value):
    cmd = "write,{address},{value}".format(address=address, value=value)
    return __HEAD + cmd


def get_register(address):
    cmd = "read,{address}".format(address=address)
    return __HEAD + cmd


def set_frequency_point(value):
    cmd = "set_freq,{value}".format(value=value)
    return __HEAD + cmd


def get_frequency_point():
    cmd = "read_freq"
    return __HEAD + cmd


def hold_baseband():
    cmd = "hold"
    return __HEAD + cmd


def release_baseband():
    cmd = "release"
    return __HEAD + cmd


def set_qam(value):
    if type(value) != int:
        raise TypeError("Frequency Power must <type 'int'>, but now is \"%s\"" % type(value))
    if value not in range(4):
        raise ValueError("Frequency Power must in range (0-3), but now is \"%s\"" % value)
    cmd = "write_qam,{value}".format(value=value)
    return __HEAD + cmd


def get_qam():
    cmd = "read_qam"
    return __HEAD + cmd


def get_br_bler():
    cmd = "read_br_bler"
    return __HEAD + cmd


def get_slot_bler():
    cmd = "read_slot_bler"
    return __HEAD + cmd


def set_tx_mode_20m():
    cmd = "set_tx_mode_20m"
    return __HEAD + cmd


def set_rx_mode_20m():
    cmd = "set_rx_mode_20m"
    return __HEAD + cmd


def is_instrument_connected():
    cmd = "check_connection"
    return __HEAD + cmd


def set_signal_0(value):  # 0:OFF 1:ON
    cmd = "operate_ant0,{value}".format(value=value)
    return __HEAD + cmd


def set_signal_1(value):
    cmd = "operate_ant1,{value}".format(value=value)
    return __HEAD + cmd


def get_signal_status(idx):
    cmd = "get_ant{idx}_pa_status".format(idx=idx)
    return __HEAD + cmd


def reboot():
    return "dfm_test_reboot"


def set_serial_number(value):
    return "set_serial_number({value})".format(value=value)


def get_serial_number():
    return "get_serial_number"


def load_protocol_stack():
    return "dfm_test_end"


def unload_protocol_stack():
    return "dfm_test_start"


def set_flag_result(flag, result):
    return "set_flag_result({flag},{result})".format(flag=flag, result=result)


def get_flag_result(flag):
    return "get_flag_result({flag})".format(flag=flag)


def get_all_flag_result():
    return "get_all_flag_result"


def is_button_clicked():
    return "is_button_clicked"


def is_uart_connected():
    return "is_uart_connect"


def is_usb_connected():
    return "is_usb_connect"


def start_web_server():
    return "dfm_websever_start"


def stop_web_server():
    return "dfm_websever_stop"


def reset_button_click():
    return "reset_button_click"


def get_calibration_value(band, level):  # 获取协议栈的校准值
    cmd = "get_table_refgain_targetpwr,{band},{level}".format(band=band, level=level)
    return __HEAD + cmd


def set_tssi_time_interval(interval=1):
    value = {1: "00", 2: "01", 3: "10", 4: "11"}.get(interval)
    cmd = "set_tssi_time_option,{value}".format(value=value)
    return __HEAD + cmd


def read_gain_pwr(is5G=True):  # 获取AB路的增益
    band = 1 if is5G is True else 0
    cmd = "read_rf2g5g_pwr,{band}".format(band=band)
    return __HEAD + cmd


def get_calibration_data():
    return "get_calibration_data"


def set_calibration_data(data):
    return "set_calibration_data({data})".format(data=data)


def set_bandwidth(value):
    cmd = "set_bw,{value}".format(value=value)
    return __HEAD + cmd


def get_bandwidth():
    cmd = "get_bw"
    return __HEAD + cmd
