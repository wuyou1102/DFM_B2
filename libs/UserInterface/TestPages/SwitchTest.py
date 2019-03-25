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
        desc = wx.StaticText(self, wx.ID_ANY, "请按下治具上的开关", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        desc.SetFont(Font.DESC)
        desc.SetBackgroundColour(Color.LightSkyBlue1)
        self.output = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.output.SetInsertionPointEnd()
        sizer.Add(desc, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def before_test(self):
        super(Switch, self).before_test()
        uart = self.get_communicat()
        uart.reset_button_click()
        self.stop_flag = True
        self.output.SetValue("")

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
            state = u"已触发" if result else u"未触发"
            self.append_log(u"查询开关状态 \"%s\"" % state)
            if result:
                self.append_log(u"测试通过，请点击PASS。")
                self.EnablePass()
                break
            self.Sleep(1)

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    @staticmethod
    def GetName():
        return u"开关测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.PCBA_SWITCH
        elif t in ["MACHINE", u"整机"]:
            return String.MACHINE_SWITCH
