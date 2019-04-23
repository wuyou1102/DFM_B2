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
    def __init__(self, parent, type, freq):
        self.freq = freq
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.init_minimum_and_maximum()

    def GetSignalAnalyzer(self):
        return self.Parent.Parent.Parent.Parent.SignalAnalyzer

    def init_minimum_and_maximum(self):
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer")
        self.a_min = float(config.get('%sa(min)' % self.freq))
        self.a_max = float(config.get('%sa(max)' % self.freq))
        self.b_min = float(config.get('%sb(min)' % self.freq))
        self.b_max = float(config.get('%sb(max)' % self.freq))
        logger.info(u"{freq}: A({ai}-{aa})  B({bi}-{ba})".format(freq=self.freq,
                                                                 ai=self.a_min, aa=self.a_max,
                                                                 bi=self.b_min, ba=self.b_max))

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 0, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_ant_sizer(), 1, wx.EXPAND | wx.LEFT, 5)
        hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, 5)
        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.LEFT, 15)
        sizer.Add(self.__init_scroll_bar(), 0, wx.EXPAND | wx.LEFT, 15)
        self.message = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.message, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1), wx.TE_READONLY)
        button = wx.Button(self, wx.ID_ANY, u"重设频点", wx.DefaultPosition, (65, 27), 0, name=str(self.freq))
        button.Bind(wx.EVT_BUTTON, self.on_freq_point_selected)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def __init_ant_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.signal_0 = wx.CheckBox(self, wx.ID_ANY, u"A路", wx.DefaultPosition, wx.DefaultSize, 0, name='0')
        self.signal_1 = wx.CheckBox(self, wx.ID_ANY, u"B路", wx.DefaultPosition, wx.DefaultSize, 0, name='1')
        self.signal_0.Bind(wx.EVT_CHECKBOX, self.on_check_box)
        self.signal_1.Bind(wx.EVT_CHECKBOX, self.on_check_box)
        sizer.Add(self.signal_0, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.signal_1, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def on_check_box(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        self.set_signal_on_off(idx=name, ON=obj.IsChecked())

    def set_signal_on_off(self, idx, ON=True):
        comm = self.get_communicate()
        if int(idx) == 0:
            comm.set_signal_0(ON=ON)
            self.Sleep(0.05)
            self.signal_0.SetValue(comm.is_signal_opened(0))
        else:
            comm.set_signal_1(ON=ON)
            self.Sleep(0.05)
            self.signal_1.SetValue(comm.is_signal_opened(1))

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_communicate()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def update_current_signal_status(self):
        def update_signal():
            self.Sleep(0.05)
            comm = self.get_communicate()
            self.signal_0.SetValue(comm.is_signal_opened(0))
            self.signal_1.SetValue(comm.is_signal_opened(1))

        Utility.append_thread(target=update_signal, allow_dupl=True)

    def update_current_info(self):
        def update_info():
            self.Sleep(0.05)
            comm = self.get_communicate()
            freq = comm.get_frequency_point()
            self.current_point.SetValue(freq)
            if float(freq) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")
            power = comm.get_radio_frequency_power()
            self.slider.SetValue(power)
            self.static_text.SetLabel(hex(power).upper())
            self.signal_0.SetValue(comm.is_signal_opened(0))
            self.signal_1.SetValue(comm.is_signal_opened(1))

        Utility.append_thread(target=update_info, allow_dupl=True)

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_communicate()
        uart.set_qam(value=selected)
        self.update_current_mcs()

    def __init_status_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        restart = wx.BitmapButton(self, wx.ID_ANY, Picture.restart, wx.DefaultPosition, (33, 33), 0)
        restart.Bind(wx.EVT_BUTTON, self.on_restart)
        sizer.Add(restart, 0, wx.ALL, 1)
        return sizer

    def __init_mcs_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"调制方式: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_mcs = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     ["BPSK", "QPSK", "16QAM", "64QAM"], 0)
        self.current_mcs.Bind(wx.EVT_CHOICE, self.on_mcs_selected)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_mcs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

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
        comm.set_radio_frequency_power(15)
        self.update_current_info()
        ctrls = [self.slider, self.signal_0, self.signal_1, self.PassButton]
        if self.GetSignalAnalyzer() is not None:
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

    def __test_road(self, index=0):
        name = 'a' if index == 0 else 'b'
        minimum = self.a_min if index == 0 else self.b_min
        maximum = self.a_max if index == 0 else self.b_max
        comm = self.get_communicate()
        if index == 0:
            comm.set_signal_0(ON=True)
            comm.set_signal_1(ON=False)
        else:
            comm.set_signal_0(ON=False)
            comm.set_signal_1(ON=True)
        self.update_current_signal_status()
        for i in range(5):
            for _ in range(150):
                if self.stop_flag:
                    return None
                time.sleep(0.01)
            try:
                txp = self.get_transmit_power()
            except Exception as e:
                self.LogMessage(u"[%s] 当前测试%s路发送功率为：%s" % (i, name.upper(), e.message))
                continue
            self.LogMessage(u"[%s] 当前测试%s路发送功率为：%s" % (i, name.upper(), txp))
            if minimum < txp < maximum:
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

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_communicate()
            uart.hold_baseband()
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
        finally:
            obj.Enable()

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def on_scroll_changed(self, event):
        x = self.slider.GetValue()
        uart = self.get_communicate()
        uart.set_radio_frequency_power(value=x)
        self.Sleep(0.2)
        self.update_current_power()

    def on_scroll(self, event):
        x = self.slider.GetValue()
        self.static_text.SetLabel(hex(x).upper())

    def __init_scroll_bar(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_name = wx.StaticText(self, wx.ID_ANY, u"射频功率:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.slider = wx.Slider(self, wx.ID_ANY, 0, 0, 31, wx.DefaultPosition, wx.DefaultSize,
                                wx.SL_HORIZONTAL | wx.SL_SELRANGE | wx.SL_TICKS)
        self.slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_scroll_changed)
        self.slider.Bind(wx.EVT_SLIDER, self.on_scroll)
        self.static_text = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, (30, -1), 0)
        sizer.Add(title_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(self.slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(self.static_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        return sizer

    def LogMessage(self, msg):
        msg = u"{time}:{message}\n".format(time=Utility.get_timestamp(), message=msg.strip('\r\n'))
        wx.CallAfter(self.message.AppendText, msg)
        comm = self.get_communicate()
        if comm is None:
            return
        with open(os.path.join(Path.TEST_LOG_SAVE, "%s.log" % comm.SerialNumber), 'a') as log:
            log.write(msg)
