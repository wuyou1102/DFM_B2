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
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)  # 绑定一个定时器事件

    def OnTimer(self, event):
        comm = self.get_communicate()
        if comm.is_usb_connected():
            self.EnablePass()

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.desc = wx.StaticText(self, wx.ID_ANY, u"请插入U盘", wx.DefaultPosition, wx.DefaultSize, 0)
        self.desc.SetFont(Font.DESC)
        self.desc.SetBackgroundColour(Color.LightSkyBlue1)
        sizer.Add(self.desc, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 1)
        return sizer

    def before_test(self):
        super(USB, self).before_test()

    def start_test(self):
        self.FormatPrint(info="Started")
        self.timer.Start(100)

    def stop_test(self):
        self.timer.Stop()
        self.FormatPrint(info="Stop")

    @staticmethod
    def GetName():
        return u"USB测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.USB_PCBA
        elif t in ["MACHINE", u"整机"]:
            return String.USB_MACH
