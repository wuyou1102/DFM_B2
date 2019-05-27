# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import String

logger = logging.getLogger(__name__)


class Calibration(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        return sizer

    def before_test(self):
        super(Calibration, self).before_test()
        self.stop_flag = True

    def start_test(self):
        Utility.append_thread(target=self.ping)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    @staticmethod
    def GetName():
        return u"校准数据测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.PCBA_ETHERNET
        elif t in ["MACHINE", u"整机"]:
            return String.MACHINE_ETHERNET
