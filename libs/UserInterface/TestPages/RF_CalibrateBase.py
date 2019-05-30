# -*- encoding:UTF-8 -*-
import logging
import os
import wx
import time
import Base
from libs import Utility
from libs.Config import Path

logger = logging.getLogger(__name__)
FREQ_5G = 5800


class CalibrateBase(Base.TestPage):
    def __init__(self, parent, type, freq):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.FREQ = freq
        self.INITIAL_DATA = Utility.CLOSE_LOOP_INITIAL_VALUE.get(freq)
        self.MAX_LEVEL = max(self.INITIAL_DATA.keys())
        self.MIN_LEVEL = min(self.INITIAL_DATA.keys())
        self.GAIN_UNIT = self.get_gain_unit()
        self.GAIN_GAP_0, self.GAIN_GAP_1, = self.get_gain_gap()
        self.POWER_UNIT = 1.0 / 3
        self.FLAG_5G = True if self.FREQ == FREQ_5G else False
        option = "5800gain" if freq == FREQ_5G else "2400gain"
        self.SA_GAIN = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer", option=option)  # 频谱仪增益

    def get_gain_unit(self):
        raise NotImplementedError

    def get_gain_gap(self):
        raise NotImplementedError

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
        comm.set_frequency_point(self.FREQ * 1000)
        comm.set_tssi_time_interval(interval=1)
        # comm.set_signal_0(ON=True)
        comm.set_signal_1(ON=False)

        if self.GetSignalAnalyzer() is not None:
            self.GetSignalAnalyzer().SetFrequency(self.FREQ)
            self.GetSignalAnalyzer().SetCorrOffs(self.SA_GAIN)
            self.PassButton.Disable()

    def start_test(self):
        if self.GetSignalAnalyzer() is None:
            self.manual_calibration()
        else:
            Utility.append_thread(target=self.automatic_calibration)

    def get_current_tssi(self):
        if self.GetSignalAnalyzer() is None:
            tssi = self.get_tssi_input()
        else:
            tssi = self.get_transmit_power()
        try:
            tssi_value = float(tssi)
            self.LogMessage(u"得到的TSSI值输入：\"%s\"" % tssi)
            return tssi_value
        except ValueError and TypeError:
            self.LogMessage(u"异常的TSSI值输入：\"%s\"" % tssi)
            return None

    def __calibrate_1(self, data):  # 一共校准两次 第一次gain和power都校准
        self.set_gain_and_power(*data.get(self.MAX_LEVEL))

        tssi = self.get_current_tssi()
        if tssi is None:
            return None
        else:
            if self.MAX_LEVEL - 3 <= tssi <= self.MAX_LEVEL + 3:
                gain_8003s = int(self.get_current_gain(A=True), 16)
                gain_gap = int(round((self.MAX_LEVEL - tssi) / self.GAIN_UNIT)) + (
                        data.get(self.MAX_LEVEL)[0] - gain_8003s)
                power_gap = int(round((self.MAX_LEVEL - tssi) / self.POWER_UNIT))
                tmp = dict()
                for _ in range(self.MAX_LEVEL, self.MIN_LEVEL - 1, -1):
                    ori_gain, ori_power = data.get(_)
                    cali_gain, cali_power = ori_gain - gain_gap, ori_power + power_gap
                    tmp[_] = (cali_gain, cali_power)
                    if _ in [self.MAX_LEVEL, self.MIN_LEVEL]:
                        self.LogMessage(u"[第一次校准数据]<%02d>: %05s | %05s" % (_, hex(cali_gain), hex(cali_power)))
                return tmp
            else:
                return False

    def __calibrate_2(self, data):
        if data is False or data is None:
            return data
        self.set_gain_and_power(*data.get(self.MAX_LEVEL))
        tssi = self.get_current_tssi()
        if tssi is None:
            return None
        else:
            if self.MAX_LEVEL - 0.5 <= tssi <= self.MAX_LEVEL + 0.5:
                gain_8003s = int(self.get_current_gain(A=True), 16)
                gain = self.INITIAL_DATA.get(self.MAX_LEVEL)[0]
                gain_lower = gain + self.GAIN_GAP_0
                gain_upper = gain + self.GAIN_GAP_1
                if gain_lower <= gain_8003s <= gain_upper:
                    self.LogMessage(u"当前增益\"%s\"在范围 [%s-%s]内" % (gain_8003s, gain_lower, gain_upper))
                    power_gap = int(round((self.MAX_LEVEL - tssi) / self.POWER_UNIT))
                    gain_gap = gain_8003s - int(data.get(self.MAX_LEVEL)[0])
                    print gain_gap
                    for _ in range(self.MAX_LEVEL, self.MIN_LEVEL - 1, -1):
                        ori_gain, ori_power = data.get(_)
                        cali_gain, cali_power = ori_gain + gain_gap, ori_power + power_gap
                        data[_] = (cali_gain, cali_power)
                        if _ in [self.MAX_LEVEL, self.MIN_LEVEL]:
                            self.LogMessage(u"[第一次校准数据]<%02d>: %05s | %05s" % (_, hex(cali_gain), hex(cali_power)))
                    return data
                else:
                    self.LogMessage(u"异常:当前增益\"%s\"不在范围 [%s-%s]内" % (gain_8003s, gain_lower, gain_upper))
                    return False
            else:
                return False

    def get_current_gain(self, A=True):
        device = self.get_communicate()
        device.disable_spi()
        gain_8003s = device.get_8003s_gain_power(self.FLAG_5G)
        device.enable_spi()
        if gain_8003s == "0000000000000000":
            self.LogMessage(u'从寄存器获取的8003S的值异常，重新获取')
            return self.get_current_gain(A=A)
        else:
            value = gain_8003s[-2:] if A else gain_8003s[-4:-2]
            self.LogMessage(u'从寄存器获取的8003S的值为：[%s]' % value)
            return value

    def set_gain_and_power(self, gain, power):
        device = self.get_communicate()
        self.LogMessage(u'设置寄存器：[%s]:[%s]' % (hex(gain), hex(power)))
        if self.FLAG_5G:
            device.disable_tssi_5g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_5g()
        else:
            device.disable_tssi_2g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_2g()
        self.LogMessage(u'获取寄存器的设置值：%s' % device.get_gain_and_power())
        self.LogMessage(u'获取寄存器的设置值：%s' % self.get_current_gain(True))

    def manual_calibration(self):
        data = self.__calibrate_1(data=self.INITIAL_DATA)
        cali_value = self.__calibrate_2(data=data)
        if cali_value is None:
            self.LogMessage(u"数据获取失败")
        elif cali_value is False:
            self.LogMessage(u"校准失败")
        else:
            self.LogMessage(u"校准成功")
            self.set_calibration_data(data=cali_value)

    def automatic_calibration(self):
        try:
            data = self.__calibrate_1(data=self.INITIAL_DATA)
            cali_value = self.__calibrate_2(data=data)
            if cali_value is None:
                self.LogMessage(u"数据获取失败")
                return
            elif cali_value is False:
                self.LogMessage(u"校准失败")
                self.SetResult("FAIL")
                return
            else:
                self.LogMessage(u"校准成功")
                self.set_calibration_data(data=cali_value)
                self.SetResult("PASS")
                return
        except StopIteration:
            return

    def set_calibration_data(self, data):
        cali_list = self.convert_cali_dict2list(data=data)
        device = self.get_communicate()
        ori_list = device.get_calibration_data()
        if self.FLAG_5G:
            ori_list[32:64] = cali_list
        else:
            ori_list[0:32] = cali_list
        device.set_calibration_data(",".join(ori_list))

    @staticmethod
    def convert_cali_dict2list(data):
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
        self.sleep(0.8)
        lst = list()
        for x in range(10):
            self.sleep(0.2)
            value = self.__get_transmit_power()
            # self.LogMessage(u"[%02d]从仪器上取值为：\"%s\"" % (x + 1, value))
            lst.append(value)
        self.LogMessage(u"去掉最小值/最大值：[%s/%s]" % (min(lst), max(lst)))
        lst.remove(max(lst))
        lst.remove(min(lst))
        avg = sum(lst) / len(lst)
        self.LogMessage(repr(lst))
        self.LogMessage(u"平均值为：%s" % avg)
        return avg

    def __get_transmit_power(self):
        try:
            result = self.GetSignalAnalyzer().GetBurstPower()
            result = result.split(',')[2]
            _lst = result.split('E')
            value, power = _lst[0], _lst[1]
            value = round(float(value), 3)
            power = pow(10, int(power))
            return value * power
        except Exception as e:
            logger.error(e.message)
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

    def sleep(self, sec):
        for _ in range(int(sec * 100)):
            if self.stop_flag:
                raise StopIteration
            time.sleep(0.01)
