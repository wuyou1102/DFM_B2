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
        option = "2400gain" if self.freq == 2400 else "5800gain"
        self.gain = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer", option=option)

    def GetSignalAnalyzer(self):
        return self.Parent.Parent.Parent.Parent.SignalAnalyzer

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 0, wx.EXPAND, 0)
        # hori_sizer.Add(self.__init_ant_sizer(), 1, wx.EXPAND | wx.LEFT, 5)
        # hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, 5)
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
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1), wx.TE_READONLY)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(create_button(u"重设频点", "set_freq"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(create_button(u"最大功率", "set_max_level"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(create_button(u"最小功率", "set_min_level"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "":
            print self.freq

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_communicate()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def update_current_info(self):
        self.update_current_freq_point()

    def update_current_freq_point(self):
        def update_freq():
            self.Sleep(0.05)
            comm = self.get_communicate()
            value = comm.get_frequency_point()
            self.current_point.SetValue(value)
            if float(value) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")

        Utility.append_thread(target=update_freq, allow_dupl=True)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_communicate()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs, allow_dupl=True)

    def update_current_power(self):
        def update_power():
            self.Sleep(0.05)
            comm = self.get_communicate()
            value = comm.get_radio_frequency_power()
            self.slider.SetValue(value)
            self.static_text.SetLabel(hex(value).upper())

        Utility.append_thread(target=update_power, allow_dupl=True)

    def before_test(self):
        self.stop_flag = False
        self.message.SetValue("")
        comm = self.get_communicate()
        comm.set_tx_mode_20m()
        comm.set_frequency_point(self.freq * 1000)
        self.update_current_info()
        ctrls = [self.PassButton]
        if self.GetSignalAnalyzer() is not None:
            self.GetSignalAnalyzer().SetCorrOffs(self.gain)
            for ctrl in ctrls:
                ctrl.Disable()
        else:
            for ctrl in ctrls:
                ctrl.Enable()

    def start_test(self):
        self.FormatPrint(info="Started")
        Utility.append_thread(self.transmit_test, thread_name="transmit_test_%s" % self.freq)

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
            comm.set_frequency_point("%s000" % self.freq)
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
        road0 = self.__test_road(0)
        road1 = self.__test_road(1)
        if road0 is None or road1 is None:
            return
        if road0 and road1:
            self.SetResult("PASS")
            return
        self.SetResult("FAIL")
        return

    def get_transmit_power(self):
        result = self.GetSignalAnalyzer().GetBurstPower()
        result = result.split(',')[2]
        _lst = result.split('E')
        value, power = _lst[0], _lst[1]
        value = round(float(value), 3)
        power = pow(10, int(power))
        return value * power

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
