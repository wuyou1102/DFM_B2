# -*- encoding:UTF-8 -*-
import wx
import logging
from libs.Config import Color
from libs.Config import Font
from libs.Config import Path
from libs import Utility
import os
import time
import threading

logger = logging.getLogger(__name__)
result_mapping = {
    "NotTest": "1",
    "PASS": "2",
    "FAIL": "3",
}


class Variable(object):
    __uart = None

    @classmethod
    def get_uart(cls):
        return cls.__uart

    @classmethod
    def set_uart(cls, uart=None):
        cls.__uart = uart
        return True


class TestPage(wx.Panel):
    def __init__(self, parent, type):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.lock = threading.Lock()
        self.type = type
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, self.get_name(), wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        test_sizer = self.init_test_sizer()
        result_sizer = self.init_result_sizer()
        self.main_sizer.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.main_sizer.Add(test_sizer, 1, wx.EXPAND | wx.ALL, 1)
        self.main_sizer.Add(result_sizer, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()

    def init_test_sizer(self):
        raise NotImplementedError

    def init_result_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.PassButton = self.create_result_button(True)
        self.FailButton = self.create_result_button(False)
        sizer.Add(self.PassButton, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.FailButton, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    @staticmethod
    def get_uart():
        return Variable.get_uart()

    def get_result(self):
        uart = self.get_uart()
        return uart.get_flag_result(self.get_flag())

    def get_type(self):
        return self.type

    def get_name(self):
        return self.GetName()

    @staticmethod
    def GetName():
        raise NotImplementedError

    def get_flag(self):
        return self.GetFlag(t=self.type)

    @staticmethod
    def GetFlag(t):
        raise NotImplementedError

    def Show(self):
        super(TestPage, self).Show()
        self.__parent.refresh()
        self.before_test()
        self.start_test()

    def Hide(self):
        super(TestPage, self).Hide()
        self.__parent.refresh()
        self.stop_test()

    def create_result_button(self, isPass):
        color = Color.SpringGreen3 if isPass else Color.Firebrick2
        label = u"PASS" if isPass else u"FAIL"
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0, name=label)
        button.SetBackgroundColour(color)
        button.SetFont(Font.COMMON_1_LARGE_BOLD)
        button.Bind(wx.EVT_BUTTON, self.on_result_button)
        return button

    def on_result_button(self, event):
        obj = event.GetEventObject()
        logger.debug("\"%s\" Result is : <%s>" % (self.name, obj.Name))
        if self.SetResult(result_mapping[obj.Name]):
            self.__parent.next_page()

    def before_test(self):
        self.EnablePass(enable=False)

    def start_test(self):
        print 'start_test'

    def stop_test(self):
        print 'stop_test'

    def SetResult(self, result):
        self.FormatPrint(result, symbol="=")
        uart = self.get_uart()
        if uart.set_flag_result(flag=self.get_flag(), result=result):
            return True
        return False

    def EnablePass(self, enable=True):
        self.PassButton.Enable(enable=enable)

    def LogMessage(self, msg):
        msg = msg.strip('\r\n')
        uart = self.get_uart()
        if uart is None:
            return
        with open(os.path.join(Path.LOG_SAVE, "%s.log" % uart.SerialNumber), 'a') as log:
            log.write(u"{time}:{message}\n".format(time=Utility.get_timestamp(), message=msg))

    @staticmethod
    def Sleep(secs):
        time.sleep(secs)

    def FormatPrint(self, info, symbol="*", length=50):
        if self.lock.acquire():
            try:
                body = " %s: %s" % (self.get_name(), info)
                self.LogMessage(symbol * length)
                self.LogMessage(symbol + body)
                self.LogMessage(symbol * length)
            finally:
                self.lock.release()


class ReportPage(wx.Panel):
    def __init__(self, parent, name=u"测试总结"):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.name = name
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        self.main_sizer.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.SetSizer(self.main_sizer)
        self.Layout()

    def get_name(self):
        return self.name

    def Show(self):
        super(ReportPage, self).Show()
        self.__parent.refresh()

    def Hide(self):
        super(ReportPage, self).Hide()
        self.__parent.refresh()

    def get_result(self):
        return "Report"

    def __init_PCBA_sizer(self):
        pass

    def __init_panel(self):
        pass
