# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility
from libs.Config import String

logger = logging.getLogger(__name__)


class Ethernet(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.output.SetInsertionPointEnd()
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def before_test(self):
        super(Ethernet, self).before_test()
        self.output.SetValue("")
        self.stop_flag = True

    def start_test(self):
        Utility.append_thread(target=self.ping)
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def ping(self):
        while self.stop_flag:
            command = 'ping 192.168.1.1 -n 1'
            result = Utility.execute_command(command, encoding='gb2312')
            line = result.outputs[2]
            self.append_log(line)
            if "TTL=" in line:
                self.append_log(u"测试通过，请点击PASS。")
                self.EnablePass()
                break
            self.Sleep(1)

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    @staticmethod
    def GetName():
        return u"网口测试"

    @staticmethod
    def GetFlag(t):
        if t == "PCBA":
            return String.PCBA_ETHERNET
        elif t in ["MACHINE", u"整机"]:
            return String.MACHINE_ETHERNET
