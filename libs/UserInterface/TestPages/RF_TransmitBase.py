# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import String

logger = logging.getLogger(__name__)


class TransmitTest(Base.Page):
    def __init__(self, parent, type):
        self.pic_status_connect1 = wx.Image('resource/icon/status_connect1.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.pic_status_connect2 = wx.Image('resource/icon/status_connect2.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.pic_status_disconnect = wx.Image('resource/icon/status_disconnect.png',
                                              wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.pic_restart = wx.Image('resource/icon/restart.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        Base.Page.__init__(self, parent=parent, name="发送测试", type=type)
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 1, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_mcs_sizer(), 1, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT, 0)

        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.__init_scroll_bar(), 0, wx.EXPAND | wx.ALL, 0)

        return sizer

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
            button = wx.Button(self, wx.ID_ANY, p, wx.DefaultPosition, (40, -1), 0, name=p)
            button.Bind(wx.EVT_BUTTON, self.on_freq_point_selected)
            sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_uart()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_uart()
        uart.set_qam(value=selected)
        self.update_current_mcs()

    def __init_status_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status = wx.StaticBitmap(self, wx.ID_ANY, self.pic_status_disconnect, wx.DefaultPosition, (33, 33), 0)
        restart = wx.BitmapButton(self, wx.ID_ANY, self.pic_restart, wx.DefaultPosition, (33, 33), 0)
        restart.Bind(wx.EVT_BUTTON, self.on_restart)
        sizer.Add(restart, 0, wx.ALL, 1)
        sizer.Add(self.status, 0, wx.ALL, 1)
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
            uart = self.get_uart()
            value = uart.get_frequency_point()
            self.current_point.SetValue(Utility.convert_freq_point(value=value))

        Utility.append_thread(target=update_freq)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_uart()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs)

    def update_current_power(self):
        def update_power():
            uart = self.get_uart()
            value = uart.get_radio_frequency_power()
            self.slider.SetValue(int(value, 16))
            self.static_text.SetLabel(value.upper())

        Utility.append_thread(update_power)

    def before_test(self):
        self.init_variable()
        uart = self.get_uart()
        uart.set_tx_mode_20m()
        self.update_current_freq_point()
        self.update_current_mcs()
        self.update_current_power()

    def init_variable(self):
        self.stop_flag = True

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_uart()
            uart.hold_baseband()
            self.Sleep(1)
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
        finally:
            obj.Enable()

    def refresh_status(self):
        def set_bitmap(bitmap):
            self.status.SetBitmap(bitmap)
            self.Sleep(0.55)

        def set_as_disconnect():
            set_bitmap(self.pic_status_disconnect)
            set_bitmap(wx.NullBitmap)

        def set_as_connect():
            set_bitmap(self.pic_status_connect1)
            set_bitmap(self.pic_status_connect2)

        uart = self.get_uart()
        while self.stop_flag:
            if uart.is_instrument_connected():
                set_as_connect()
            else:
                set_as_disconnect()

    def get_flag(self):
        return String.RF_TRANSMIT_2410

    def on_scroll_changed(self, event):
        x = self.slider.GetValue()
        uart = self.get_uart()
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
        self.static_text = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, (50, -1), 0)
        sizer.Add(title_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(self.slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(self.static_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        return sizer
