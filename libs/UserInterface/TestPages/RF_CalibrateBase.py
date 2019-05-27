# -*- encoding:UTF-8 -*-
import logging
import os

import wx

import Base
from libs import Utility
from libs.Config import Path

logger = logging.getLogger(__name__)


class CalibrateBase(Base.TestPage):
    def __init__(self, parent, type, freq):
        self.freq = freq
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.data = Utility.CLOSE_LOOP_INITIAL_VALUE.get(self.freq)
        self.max_level = max(self.data.keys())
        self.min_level = min(self.data.keys())
        self.gain_unit = 0.5 if self.freq == 5800 else 1.0
        self.power_unit = 0.33
        option = "2400gain" if self.freq == 2450 else "5800gain"
        self.gain = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer", option=option)

    def GetSignalAnalyzer(self):
        return self.Parent.Parent.Parent.Parent.SignalAnalyzer

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.message, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def before_test(self):
        self.stop_flag = False
        self.message.SetValue("")
        comm = self.get_communicate()
        comm.set_tx_mode_20m()
        comm.set_frequency_point(self.freq * 1000)
        comm.set_tssi_time_interval(interval=1)
        comm.set_signal_1(ON=False)
        self.set_gain_and_power(*self.data.get(self.max_level))
        if self.GetSignalAnalyzer() is not None:
            self.GetSignalAnalyzer().SetFrequency(self.freq)
            self.GetSignalAnalyzer().SetCorrOffs(self.gain)
            self.PassButton.Disable()

    def start_test(self):
        if self.GetSignalAnalyzer() is None:
            self.manual_calibration()
        else:
            Utility.append_thread(target=self.automatic_calibration)

    def analyze_tssi(self, tssi_value):
        self.LogMessage(u"得到当前 TSSI 值：\"%s\"" % tssi_value)
        try:
            tssi_value = float(tssi_value)
        except ValueError and TypeError:
            self.LogMessage(u"错误的 TSSI 输入")
            return None
        if self.max_level - 3 <= tssi_value <= self.max_level + 3:  # 最大上下限
            return self.__calibrate(tssi=tssi_value)
        else:
            self.LogMessage(u"射频信号异常，请检查确认。")
            return None

    def __calibrate(self, tssi):
        is5G = False if self.freq == 2450 else True
        gain_8003s = int(self.get_8003s_gain_power(is5G), 16)
        gain_gap = int(round((self.max_level - tssi) / self.gain_unit)) + (
                self.data.get(self.max_level)[0] - gain_8003s)
        power_gap = int(round((self.max_level - tssi) / self.power_unit))
        tmp = dict()
        for _ in range(self.max_level, self.min_level - 1, -1):
            ori_gain, ori_power = self.data.get(_)
            cali_gain, cali_power = ori_gain - gain_gap, ori_power + power_gap
            tmp[_] = (cali_gain, cali_power)
        result = self.__test_calibrate_result(*tmp.get(self.max_level))
        if result is not False:
            for _ in range(self.max_level, self.min_level - 1, -1):
                ori_gain, ori_power = tmp.get(_)
                cali_gain, cali_power = result + ori_gain, ori_power
                self.LogMessage("[%02d]: %05s | %05s" % (_, hex(cali_gain), hex(cali_power)))
                tmp[_] = (cali_gain, cali_power)
            return tmp
        return None

    def __test_calibrate_result(self, gain, power):
        self.set_gain_and_power(gain=gain, power=power)
        if self.GetSignalAnalyzer() is None:
            rssi = self.get_tssi_input()
        else:
            rssi = self.get_transmit_power()
        is5G = False if self.freq == 2450 else True
        cur_gain = int(self.get_8003s_gain_power(is5G, A=True), 16)
        try:
            rssi = float(rssi)
        except TypeError and ValueError:
            return False
        self.LogMessage(u"得到当前 TSSI 值：\"%s\"" % rssi)
        if self.max_level - 0.5 <= rssi <= self.max_level + 0.5:
            if gain - 6 <= cur_gain <= gain + 6:
                return cur_gain - gain
            self.LogMessage(u"当前增益异常请检查确认，请检查确认。")
            return False
        self.LogMessage(u"当前TSSI值异常。")
        return False

    def get_8003s_gain_power(self, is5G, A=True):
        device = self.get_communicate()
        device.disable_spi()
        gain_8003s = device.get_8003s_gain_power(is5G)
        device.enable_spi()
        value = gain_8003s[-2:] if A else gain_8003s[-4:-2]
        self.LogMessage(u'从寄存器获取的8003S的值为：[%s]' % value)
        return value

    def set_gain_and_power(self, gain, power):
        device = self.get_communicate()
        self.LogMessage(u'设置寄存器：[%s]:[%s]' % (hex(gain), hex(power)))
        if self.freq == 5800:
            device.disable_tssi_5g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_5g()
        else:
            device.disable_tssi_2g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_2g()

    def manual_calibration(self):
        rssi = self.get_tssi_input()
        cali_value = self.analyze_tssi(tssi_value=rssi)
        if cali_value is None:
            self.LogMessage(u"校准失败")
        else:
            self.set_calibration_data(data=cali_value)

    def automatic_calibration(self):
        rssi = self.get_transmit_power()
        cali_value = self.analyze_tssi(tssi_value=rssi)
        if cali_value is None:
            self.LogMessage(u"校准失败")
            self.SetResult("FAIL")
            return
        self.set_calibration_data(data=cali_value)
        self.SetResult("PASS")
        return

    def set_calibration_data(self, data):
        cali_list = self.conver_cali_dict2list(data=data)
        device = self.get_communicate()
        ori_list = device.get_calibration_data()
        if self.freq == 2450:
            ori_list[0:32] = cali_list
        else:
            ori_list[32:64] = cali_list
        device.set_calibration_data(",".join(ori_list))

    def conver_cali_dict2list(self, data):
        lst = list()
        max_level = max(data.keys())
        min_level = min(data.keys())
        for l in range(max_level, min_level - 1, -1):
            for m in data.get(l):
                lst.append(str(m))
        return lst

    def get_tssi_input(self):
        try:
            dlg = wx.TextEntryDialog(self, u'请输入仪器上的信号强度值(dBm)', u"")
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            return None
        finally:
            dlg.Destroy()

    def get_transmit_power(self):
        lst = list()
        for x in range(10):
            value = self.__get_transmit_power()
            self.LogMessage(u"[%02d]从仪器上取值为：\"%s\"" % (x + 1, value))
            lst.append(value)
        self.LogMessage(u"去掉最大值：%s" % max(lst))
        lst.remove(max(lst))
        self.LogMessage(u"去掉最大值：%s" % min(lst))
        lst.remove(min(lst))
        ret = sum(lst) / len(lst)
        self.LogMessage(u"平均值为：%s" % ret)
        return ret

    def __get_transmit_power(self):
        try:
            self.Sleep(0.2)
            result = self.GetSignalAnalyzer().GetBurstPower()
            result = result.split(',')[2]
            _lst = result.split('E')
            value, power = _lst[0], _lst[1]
            value = round(float(value), 3)
            power = pow(10, int(power))
            return value * power
        except Exception as e:
            return self.__get_transmit_power()

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def LogMessage(self, msg):
        msg = u"{time}:{message}\n".format(time=Utility.get_timestamp(), message=msg.strip('\r\n'))
        logger.info(msg)
        wx.CallAfter(self.message.AppendText, msg)
        comm = self.get_communicate()
        if comm is None:
            return
        with open(os.path.join(Path.TEST_LOG_SAVE, "%s.log" % comm.SerialNumber), 'a') as log:
            log.write(msg)
