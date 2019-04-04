# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import String
from libs import Utility
import time

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
        self.check_thread(thread=thread)

    def check_thread(self, thread):
        if thread.isAlive():
            wx.CallLater(100, self.check_thread, thread=thread)
        else:
            if not self.stop_flag:
                dlg = WaitBootUpDialog()
                dlg.show_modal()
                if dlg.GetResult():
                    socket = self.get_communicate()
                    if socket.reconnect():
                        self.EnablePass()
                else:
                    Utility.Alert.Error("启动失败，请重新连接。")
                    self.Parent.Parent.Parent.disconnect()
            else:
                logger.info(u"Watch Dog Test Is Over.")

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def wait_for_reboot(self):
        while not self.stop_flag:
            if not Utility.is_device_connected("192.168.1.1", port=51341, timeout=1):
                return
            self.Sleep(1)

    @staticmethod
    def GetName():
        return u"看门狗测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.WATCH_DOG_MACH


class WaitBootUpDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title=u"正在重启，请耐心等待。", size=(400, 300),
                           pos=wx.DefaultPosition,
                           style=wx.CAPTION)
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.message = wx.TextCtrl(self.panel, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        main_sizer.Add(self.message, 1, wx.EXPAND | wx.ALL, 1)
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Layout()

    def show_modal(self):
        Utility.append_thread(self.__wait_for_boot_up)
        self.ShowModal()

    def GetResult(self):
        return self.result

    def __wait_for_boot_up(self, timeout=120):
        try:
            for x in range(timeout):
                self.output(u"检查设备是否已经启动[%s]" % (x + 1))
                if Utility.is_device_connected(address="192.168.1.1", port=51341):
                    self.output(u"启动成功")
                    self.result = True
                    return True
            self.output(u"启动失败")
            self.result = False
            return False
        finally:
            self.Destroy()

    def output(self, msg):
        msg = "%s: %s\n" % (Utility.get_timestamp('%H:%M:%S'), msg)
        wx.CallAfter(self.message.AppendText, msg)
        time.sleep(0.005)
