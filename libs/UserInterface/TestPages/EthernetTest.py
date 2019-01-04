# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs import Utility

logger = logging.getLogger(__name__)


class EthernetTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name="网口测试", flag="Ethernet")
        self.stop_flag = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.output.SetInsertionPointEnd()
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def before_test(self):
        super(EthernetTest, self).before_test()
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
            command = 'ping 192.168.90.1 -n 1'
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
