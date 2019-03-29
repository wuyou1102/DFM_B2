# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import Font
from libs.Config import Picture

logger = logging.getLogger(__name__)


class TransmitBase(Base.TestPage):
    def __init__(self, parent, type, freq):
        self.freq = freq
        Base.TestPage.__init__(self, parent=parent, type=type)


    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 1, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, 5)
        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.LEFT, 15)
        sizer.Add(self.__init_scroll_bar(), 0, wx.EXPAND | wx.LEFT, 15)
        return sizer

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1), wx.TE_READONLY)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        button = wx.Button(self, wx.ID_ANY, u"重设频点", wx.DefaultPosition, (65, 27), 0, name=str(self.freq))
        button.Bind(wx.EVT_BUTTON, self.on_freq_point_selected)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_communicat()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_communicat()
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
            uart = self.get_communicat()
            value = uart.get_frequency_point()
            self.current_point.SetValue(value)
            if float(value) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")

        Utility.append_thread(target=update_freq, allow_dupl=True)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_communicat()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs, allow_dupl=True)

    def update_current_power(self):
        def update_power():
            uart = self.get_communicat()
            value = uart.get_radio_frequency_power()
            self.slider.SetValue(value)
            self.static_text.SetLabel(hex(value).upper())

        Utility.append_thread(target=update_power, allow_dupl=True)

    def before_test(self):
        self.init_variable()
        uart = self.get_communicat()
        uart.set_tx_mode_20m()
        uart.set_frequency_point(self.freq * 1000)
        uart.set_radio_frequency_power(15)
        self.update_current_power()
        self.update_current_freq_point()

    def init_variable(self):
        self.stop_flag = True

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_communicat()
            uart.hold_baseband()
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
        finally:
            obj.Enable()

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def on_scroll_changed(self, event):
        x = self.slider.GetValue()
        uart = self.get_communicat()
        uart.set_radio_frequency_power(value=x)
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
