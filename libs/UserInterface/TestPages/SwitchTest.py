# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from Base import Variable
from libs import Utility

logger = logging.getLogger(__name__)


class SwitchTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"开关测试", flag="Switch")


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
        super(SwitchTest, self).before_test()
        uart = Variable.get_uart()
        uart.reset_button_click()
        self.stop_flag = True
        self.output.SetValue("")

    def start_test(self):
        Utility.append_thread(target=self.is_clicked)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def is_clicked(self):
        uart = Variable.get_uart()
        while self.stop_flag:
            result = uart.get_button_click()
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