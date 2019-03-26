# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import String
from libs import Utility

logger = logging.getLogger(__name__)


class Switch(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.desc = wx.StaticText(self, wx.ID_ANY, u"请按下治具上的开关", wx.DefaultPosition, wx.DefaultSize, 0)
        self.desc.SetFont(Font.DESC)
        self.desc.SetBackgroundColour(Color.LightSkyBlue1)
        sizer.Add(self.desc, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 1)
        return sizer

    def before_test(self):
        super(Switch, self).before_test()
        self.desc.SetLabel(u"请按下治具上的开关")
        uart = self.get_communicat()
        uart.reset_button_click()
        self.stop_flag = True

    def start_test(self):
        Utility.append_thread(target=self.is_button_clicked)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def is_button_clicked(self):
        uart = self.get_communicat()
        while self.stop_flag:
            result = uart.is_button_clicked()
            if result:
                self.desc.SetLabel(u"测试通过，请点击PASS。")
                self.EnablePass()
                break

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    @staticmethod
    def GetName():
        return u"开关测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.SWITCH_PCBA
        elif t in ["MACHINE", u"整机"]:
            return String.SWITCH_MACH
