# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import Picture
from libs.Config import Path
import time
import os

logger = logging.getLogger(__name__)


class TransmitBase(Base.TestPage):
    def __init__(self, parent, type, freq, RoadA=True):
        self.freq = freq
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.max_gap = 0.5 if RoadA else 3
        self.min_gap = 1 if RoadA else 3
        self.cali_max, self.cali_min = 0, 0
        self.road = 'A' if RoadA else 'B'
        option = "2400gain" if self.freq == 2400 else "5800gain"
        self.gain = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer", option=option)

    def GetSignalAnalyzer(self):
        return self.Parent.Parent.Parent.Parent.SignalAnalyzer

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 0, wx.EXPAND, 0)
        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.LEFT, 15)
        self.message = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.message, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_freq_point_sizer(self):
        def create_button(label, name):
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (65, 27), 0, name=name)
            button.Bind(wx.EVT_BUTTON, self.on_button_click)
            return button

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                         wx.TE_READONLY | wx.TE_CENTER)
        self.gain_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                     wx.TE_READONLY | wx.TE_CENTER)
        self.power_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                      wx.TE_READONLY | wx.TE_CENTER)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        self.btn_freq = create_button(u"重设频点", "set_freq")
        sizer.Add(self.btn_freq, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        sizer.Add(self.gain_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.power_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.btn_max = create_button(u"最大功率", "set_max_level")
        self.btn_min = create_button(u"最小功率", "set_min_level")
        sizer.Add(self.btn_max, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.btn_min, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "set_freq":
            self.set_frequency_point()
        elif name == "set_max_level":
            self.set_gain_and_power(*self.cali_max)
        elif name == "set_min_level":
            self.set_gain_and_power(*self.cali_min)

    def set_frequency_point(self):
        device = self.get_communicate()
        device.set_frequency_point(self.freq * 1000)
        self.refresh_current_freq_point()

    def set_gain_and_power(self, gain, power):
        device = self.get_communicate()
        self.LogMessage(u'设置寄存器：[%s]:[%s]' % (hex(int(gain)), hex(int(power))))
        if self.freq == 5800:
            device.disable_tssi_5g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_5g()
        else:
            device.disable_tssi_2g()
            device.set_gain_and_power(gain, power)
            device.enable_tssi_2g()
        self.refresh_current_gain_power()

    def refresh_current_info(self):
        self.refresh_current_freq_point()
        self.refresh_current_gain_power()

    def refresh_current_freq_point(self):
        def get_current_freq():
            comm = self.get_communicate()
            value = comm.get_frequency_point()
            self.current_point.SetValue(value)
            if float(value) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")

        Utility.append_thread(target=get_current_freq, allow_dupl=True)

    def refresh_current_gain_power(self):
        def get_current_gain_power():
            comm = self.get_communicate()
            value = comm.get_gain_and_power()
            self.gain_ctrl.SetValue(value[-2:].upper())
            self.power_ctrl.SetValue(value[-4:-2].upper())

        Utility.append_thread(target=get_current_gain_power, allow_dupl=True)

    def __configuring_device(self):
        device = self.get_communicate()
        device.set_tx_mode_20m()  # 设置发送20M
        device.set_frequency_point(self.freq * 1000)  # 设置频点
        device.set_tssi_time_interval(interval=1)  # 设置切换时间
        device.set_signal_0(ON=False)
        device.set_signal_1(ON=False)
        if self.freq == 5800:
            device.disable_tssi_5g()
            device.set_gain_and_power(*self.cali_max)
            if self.road == "A":
                device.set_signal_0(ON=True)
            else:
                device.set_signal_1(ON=True)
            device.enable_tssi_5g()
        else:
            device.disable_tssi_2g()
            device.set_gain_and_power(*self.cali_max)
            if self.road == "A":
                device.set_signal_0(ON=True)
            else:
                device.set_signal_1(ON=True)
            device.enable_tssi_2g()
        self.refresh_current_gain_power()

        # A路和B路切换方法（后续如果外挂切换小板调试完成，可以不用切换A / B路，同时打开测试？）：
        # 由于测试A路时B路需要关闭最后一级PA，所以B路的8003S功率控制寄存器值一直会为最大值（0X00），如果直接切到B路，直接开PA有输出过大损坏PA的风险。故切换流程如下：
        # 1，将A路的PA关闭，这时候A路和B路的PA都是关闭的。
        # 3，将“user7_tssi_en_5g” / “user7_tssi_en_2g”设置为0：tssi
        # 2，将初始值和目标值修改为B路需要的值。
        # 4，打开B路的PA
        # 5，将“user7_tssi_en_5g” / “user7_tssi_en_2g”设置为1：tssi

        # enable。开启闭环控制。

    def before_test(self):
        self.stop_flag = False
        self.message.SetValue("")
        self.cali_max, self.cali_min = self.get_max_min_cali_data()
        self.__configuring_device()
        self.refresh_current_info()
        ctrls = [self.PassButton, self.btn_freq, self.btn_max, self.btn_min]
        if self.GetSignalAnalyzer() is not None:
            self.GetSignalAnalyzer().SetCorrOffs(self.gain)
            for ctrl in ctrls:
                ctrl.Disable()
        else:
            for ctrl in ctrls:
                ctrl.Enable()

    def get_max_min_cali_data(self):
        device = self.get_communicate()
        cali_data = device.get_calibration_data()
        if self.freq == 2400:
            return (cali_data[0], cali_data[1]), (cali_data[30], cali_data[31])
        return (cali_data[32], cali_data[33]), (cali_data[62], cali_data[63])

    def start_test(self):
        self.FormatPrint(info="Started")
        Utility.append_thread(self.transmit_test, thread_name="transmit_test_%s%s" % (self.freq, self.road))

    def check_frequency_point(self):
        comm = self.get_communicate()
        for x in range(10):
            if self.stop_flag:
                return
            self.LogMessage(u"当前第%s次检查频点" % (x + 1))
            value = comm.get_frequency_point()
            self.LogMessage(u"当前频点为：%s" % value)
            if float(value) == self.freq:
                self.LogMessage(u"检查通过，准备测试。")
                return True
            comm.set_frequency_point(self.freq * 1000)
        self.LogMessage(u"检查不通过，无法测试。")
        return False

    def transmit_test(self):
        signal_analyzer = self.GetSignalAnalyzer()
        if signal_analyzer is None:  # 如果没有信号分析仪 就直接退出
            return
        if not self.check_frequency_point():
            Utility.Alert(u"频点设置不正确的，无法自动测试。")
            return
        signal_analyzer.SetFrequency(self.freq)  # 设置仪器分析频点
        result_max = self.__test_max()
        result_min = self.__test_min()
        if result_max is None or result_min is None:
            return
        if result_max and result_min:
            self.SetResult("PASS")
            return
        self.SetResult("FAIL")
        return

    def __test_txp(self, lower, upper):
        self.LogMessage(u"当前测试频点功率值范围应为：[%s]-[%s]" % (lower, upper))
        for i in range(3):
            try:
                txp = self.get_transmit_power()
                self.LogMessage(u"[%s]次测试结果为：%s" % (i, txp))
                if lower <= txp <= upper:
                    return True
                else:
                    self.sleep(1)
            except Exception as e:
                self.LogMessage(u"当前测试结果为：%s" % e.message)
                self.sleep(0.5)
        return False

    def __test_8003s_gain(self):
        lower, upper = 3, 15
        self.LogMessage(u"当前测试频点增益范围应为：[%s]-[%s]" % (lower, upper))
        gain = int(self.get_8003s_gain_power(), 16)
        self.LogMessage(u'从寄存器获取的8003S的[%s]路的值为：[%s]' % (self.road, gain))
        if lower <= gain <= upper:
            return True
        return False

    def __test_max(self):
        self.set_gain_and_power(*self.cali_max)
        value = 18 if self.freq == 2400 else 24
        lower, upper = value - self.max_gap, value + self.max_gap
        self.sleep(2)
        txp_result = self.__test_txp(lower=lower, upper=upper)
        gain_result = self.__test_8003s_gain()
        if txp_result and gain_result:
            return True
        return False

    def __test_min(self):
        self.set_gain_and_power(*self.cali_min)
        value = 3 if self.freq == 2400 else 9
        lower, upper = value - self.min_gap, value + self.min_gap
        self.sleep(2)
        if self.__test_txp(lower=lower, upper=upper):
            return True
        return False

    def get_transmit_power(self):
        result = self.GetSignalAnalyzer().GetBurstPower()
        result = result.split(',')[2]
        _lst = result.split('E')
        value, power = _lst[0], _lst[1]
        value = round(float(value), 3)
        power = pow(10, int(power))
        return value * power

    def get_8003s_gain_power(self):
        device = self.get_communicate()
        device.disable_spi()
        gain_8003s = device.get_8003s_gain_power()
        device.enable_spi()
        value = gain_8003s[-2:] if self.road == "A" else gain_8003s[-4:-2]
        return value

    def sleep(self, sec):
        for _ in xrange(int(sec) * 100):
            if self.stop_flag:
                return None
            time.sleep(0.01)

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def LogMessage(self, msg):
        msg = u"{time}:{message}\n".format(time=Utility.get_timestamp(), message=msg.strip('\r\n'))
        wx.CallAfter(self.message.AppendText, msg)
        comm = self.get_communicate()
        if comm is None:
            return
        with open(os.path.join(Path.TEST_LOG_SAVE, "%s.log" % comm.SerialNumber), 'a') as log:
            log.write(msg)
