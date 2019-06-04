# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import Path
import time
import os

logger = logging.getLogger(__name__)
FREQ_5G = 5800


class TransmitBase(Base.TestPage):
    def __init__(self, parent, type, freq, RoadA=True):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.FREQ = freq
        self.FLAG_ROAD_A = RoadA
        self.FLAG_5G = True if self.FREQ == FREQ_5G else False

        self.MAX_LEVEL_GAP = 1 if RoadA else 3
        self.MIN_LEVEL_GAP = 1.5 if RoadA else 3
        self.cali_max, self.cali_min = 0, 0
        option = "5800gain" if self.FLAG_5G else "2400gain"
        self.SA_GAIN = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer", option=option)

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
        # self.gain_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
        #                              wx.TE_READONLY | wx.TE_CENTER)
        # self.power_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
        #                               wx.TE_READONLY | wx.TE_CENTER)
        self.gain_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                     wx.TE_CENTER)
        self.power_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                      wx.TE_CENTER)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        self.btn_freq = create_button(u"重设频点", "set_freq")
        sizer.Add(self.btn_freq, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        sizer.Add(self.gain_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.power_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.btn_max = create_button(u"最大功率", "set_max_level")
        self.btn_min = create_button(u"最小功率", "set_min_level")
        self.btn_set = create_button(u"设置", "set")
        sizer.Add(self.btn_max, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.btn_min, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.btn_set, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

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
        elif name == "set":
            gain = int(self.gain_ctrl.GetValue(), 16)
            power = int(self.power_ctrl.GetValue(), 16)
            self.set_gain_and_power(gain, power)

    def set_frequency_point(self):
        device = self.get_communicate()
        device.set_frequency_point(self.FREQ * 1000)
        self.refresh_current_freq_point()

    def set_gain_and_power(self, gain, power):
        device = self.get_communicate()
        self.LogMessage(u'设置寄存器：[%s]:[%s]' % (hex(int(gain)), hex(int(power))))
        if self.FLAG_5G:
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
            if float(value) != self.FREQ:
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
        device.set_frequency_point(self.FREQ * 1000)  # 设置频点
        device.set_tssi_time_interval(interval=1)  # 设置切换时间
        device.set_signal_0(ON=False)
        device.set_signal_1(ON=False)
        if self.FLAG_5G:
            device.disable_tssi_5g()
            device.set_gain_and_power(*self.cali_max)
            if self.FLAG_ROAD_A:
                device.set_signal_0(ON=True)
            else:
                device.set_signal_1(ON=True)
            device.enable_tssi_5g()
        else:
            device.disable_tssi_2g()
            device.set_gain_and_power(*self.cali_max)
            if self.FLAG_ROAD_A:
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
            self.GetSignalAnalyzer().SetCorrOffs(self.SA_GAIN)
            self.GetSignalAnalyzer().SetFrequency(self.FREQ)  # 设置仪器分析频点
            for ctrl in ctrls:
                ctrl.Disable()
        else:
            for ctrl in ctrls:
                ctrl.Enable()

    def get_max_min_cali_data(self):
        device = self.get_communicate()
        cali_data = device.get_calibration_data()
        if self.FLAG_5G:
            return (cali_data[32], cali_data[33]), (cali_data[62], cali_data[63])
        return (cali_data[0], cali_data[1]), (cali_data[30], cali_data[31])

    def get_middle_cali_data(self):
        device = self.get_communicate()
        cali_data = device.get_calibration_data()
        if self.FLAG_5G:
            return cali_data[46], cali_data[47]
        return cali_data[14], cali_data[15]

    def start_test(self):
        self.FormatPrint(info="Started")
        thread_name = "TransmitTest%sA" % self.FREQ if self.FLAG_ROAD_A else "TransmitTest%sB" % self.FREQ
        Utility.append_thread(self.transmit_test, thread_name=thread_name)

    def check_frequency_point(self):
        comm = self.get_communicate()
        for x in range(10):
            if self.stop_flag:
                return
            self.LogMessage(u"当前第%s次检查频点" % (x + 1))
            value = comm.get_frequency_point()
            self.LogMessage(u"当前频点为：%s" % value)
            if float(value) == self.FREQ:
                self.LogMessage(u"检查通过，准备测试。")
                return True
            comm.set_frequency_point(self.FREQ * 1000)
        self.LogMessage(u"检查不通过，无法测试。")
        return False

    def transmit_test(self):
        signal_analyzer = self.GetSignalAnalyzer()
        if signal_analyzer is None:  # 如果没有信号分析仪 就直接退出
            return
        if not self.check_frequency_point():
            Utility.Alert(u"频点设置不正确的，无法自动测试。")
            return

        result_max = self.__test_max()
        result_min = self.__test_min()
        # result_middle = self.__test_middle()

        if result_max is None or result_min is None:
            return
        if result_max and result_min:
            self.SetResult("PASS")
            return
        else:
            self.SetResult("FAIL")
            return

    def __test_txp(self, lower, upper):
        try:
            txp = self.get_transmit_power()
            self.LogMessage(u"当前测试功率为：%s (%s-%s)" % (txp, lower, upper))
            if lower <= txp <= upper:
                return True
            return False
        except StopIteration:
            return None

    def __test_8003s_gain(self):
        if self.FLAG_5G:
            lower, upper = 3, 15
        else:
            lower, upper = 9, 15
        self.LogMessage(u"当前测试频点增益范围应为：[%s]-[%s]" % (lower, upper))
        gain = int(self.get_current_gain(self.FLAG_ROAD_A), 16)
        self.LogMessage(u'从寄存器获取的8003S的值为：[%s]' % gain)
        if lower <= gain <= upper:
            return True
        return False

    def __test_max(self):
        self.LogMessage("====================最大值测试====================")
        self.set_gain_and_power(*self.cali_max)
        value = 24 if self.FLAG_5G else 18
        lower, upper = value - self.MAX_LEVEL_GAP, value + self.MAX_LEVEL_GAP
        txp_result = self.__test_txp(lower=lower, upper=upper)
        gain_result = self.__test_8003s_gain()
        if txp_result is None:
            return None
        if txp_result and gain_result:
            return True
        return False

    def __test_min(self):
        self.LogMessage("====================最小值测试====================")
        self.set_gain_and_power(*self.cali_min)
        value = 9 if self.FLAG_5G else 3
        lower, upper = value - self.MIN_LEVEL_GAP, value + self.MIN_LEVEL_GAP
        return self.__test_txp(lower=lower, upper=upper)

    def __test_middle(self):
        self.LogMessage("====================中间值测试====================")
        self.set_gain_and_power(*self.get_middle_cali_data())
        value = 17 if self.FLAG_5G else 11
        lower, upper = value - self.MIN_LEVEL_GAP, value + self.MIN_LEVEL_GAP
        return self.__test_txp(lower=lower, upper=upper)

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

    def sleep(self, sec):
        for _ in range(int(sec * 100)):
            if self.stop_flag:
                raise StopIteration
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
