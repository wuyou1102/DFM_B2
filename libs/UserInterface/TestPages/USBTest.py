# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import String
from libs import Utility

logger = logging.getLogger(__name__)


class USB(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.AUTO = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.desc = wx.StaticText(self, wx.ID_ANY, u"请插入U盘", wx.DefaultPosition, wx.DefaultSize, 0)
        self.desc.SetFont(Font.DESC)
        self.desc.SetBackgroundColour(Color.LightSkyBlue1)
        sizer.Add(self.desc, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 1)
        return sizer

    def before_test(self):
        super(USB, self).before_test()
        self.stop_flag = True

    def start_test(self):
        Utility.append_thread(target=self.is_usb_connected)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def is_usb_connected(self):
        comm = self.get_communicat()
        while self.stop_flag:
            self.Sleep(0.05)
            result = comm.is_usb_connected()
            if result:
                self.EnablePass()
                break

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    @staticmethod
    def GetName():
        return u"USB测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.USB_PCBA
        elif t in ["MACHINE", u"整机"]:
            return String.USB_MACH
