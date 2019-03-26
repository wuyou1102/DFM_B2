# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import String

logger = logging.getLogger(__name__)


class Light(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.count = 0

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        output = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        output.AppendText(u"请检查治具上的指示灯是否全亮\n")
        output.AppendText(u"\n")
        output.AppendText(u"判断条件:\n")
        output.AppendText(u"  指示灯全亮  PASS\n")
        output.AppendText(u"  其他情况    FAIL\n")
        output.SetInsertionPointEnd()
        output.SetBackgroundColour(Color.LightSkyBlue1)
        output.SetFont(Font.COMMON_1_LARGE_BOLD)
        sizer.Add(output, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def before_test(self):
        pass

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")

    @staticmethod
    def GetName():
        return u"灯座测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.LAMP_HOLDER_PCBA
