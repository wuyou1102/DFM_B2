# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import String

logger = logging.getLogger(__name__)


class TransmitTest(Base.Page):
    def __init__(self, parent, type):
        Base.Page.__init__(self, parent=parent, name="发送测试", type=type)
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_freq_point_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def before_test(self):
        pass

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        sizer.Add(title, 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.current_point, 0, wx.EXPAND | wx.ALL, 1)
        for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
            button = wx.Button(self, wx.ID_ANY, p, wx.DefaultPosition, (40, -1), 0, name=p)
            button.Bind(wx.EVT_BUTTON, self.on_freq_point_selected)
            sizer.Add(button, 0, wx.ALL, 1)
        return sizer

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_uart()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def __init_freq_power_sizer(self):
        pass

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")

    def get_flag(self):
        return String.RF_TRANSMIT
