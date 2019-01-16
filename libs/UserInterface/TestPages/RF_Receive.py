# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import String
from Base import Variable

logger = logging.getLogger(__name__)


class ReceiveTest(Base.Page):
    def __init__(self, parent, type):
        Base.Page.__init__(self, parent=parent, name="接收测试", type=type)
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        return sizer

    def __init_freq_point_sizer(self):

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.port_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, Utility.Serial.list_ports(),0)
        sizer.Add(title, 0, wx.EXPAND | wx.TOP, 5)
        title.Add(self.port_choice, 1, wx.EXPAND | wx.ALL, 1)


        for p in ['2410', '2450', '2475','5750', '5800', '5825']:
            print p
        return sizer

    def before_test(self):
        self.stop_flag = True
        uart = self.get_uart()
        uart.set_rx_mode_20m()

    def start_test(self):
        Utility.append_thread(target=self.draw_line)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def draw_line(self):
        uart = self.get_uart()
        while self.stop_flag:
            print uart.get_slot_bler()
            self.Sleep(1)

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    def get_flag(self):
        return String.RF_RECEIVE
