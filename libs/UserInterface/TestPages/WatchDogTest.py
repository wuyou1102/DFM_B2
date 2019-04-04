# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import String
from libs import Utility

logger = logging.getLogger(__name__)


class WatchDog(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.AUTO = True

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.desc = wx.StaticText(self, wx.ID_ANY, u"请长按按键6秒后松开", wx.DefaultPosition, wx.DefaultSize, 0)
        self.desc.SetFont(Font.DESC)
        self.desc.SetBackgroundColour(Color.LightSkyBlue1)
        sizer.Add(self.desc, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 1)
        return sizer

    def before_test(self):
        super(WatchDog, self).before_test()
        self.stop_flag = False

    def start_test(self):
        self.FormatPrint(info="Started")
        thread = Utility.append_thread(self.wait_for_reboot)
        thread.join()

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def wait_for_reboot(self):
        while not self.stop_flag:
            if not Utility.is_device_connected("192.168.1.1", port=51341, timeout=1):
                break
            self.Sleep(1)
        # self.wait_for_boot_up(timeout=200)

    def wait_for_boot_up(self, timeout=100):
        dlg = Utility.Alert.CountdownDialog("")
        dlg.Countdown(100)

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    @staticmethod
    def GetName():
        return u"看门狗测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.WATCH_DOG_MACH
