# -*- encoding:UTF-8 -*-
import wx
import logging
from libs.Config import Color
from libs.Config import Font

logger = logging.getLogger(__name__)


class Variable(object):
    __uart = None

    @classmethod
    def get_uart(cls):
        return cls.__uart

    @classmethod
    def set_uart(cls, uart=None):
        cls.__uart = uart
        return True


class Page(wx.Panel):
    def __init__(self, parent, name, flag):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.name = name
        self.flag = flag
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, self.name, wx.DefaultPosition, wx.DefaultSize,
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

    def get_name(self):
        return self.name

    def get_result(self):
        uart = self.get_uart()
        return uart.get_flag_result(self.flag)

    def Show(self):
        super(wx.Panel, self).Show()
        self.__parent.refresh()

    def Hide(self):
        super(wx.Panel, self).Hide()
        self.__parent.refresh()

    def create_result_button(self, isPass):
        color = Color.SpringGreen3 if isPass else Color.Firebrick2
        label = u"PASS" if isPass else u"FAIL"
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0)
        button.SetBackgroundColour(color)
        button.SetFont(Font.COMMON_1_LARGE_BOLD)
        button.Bind(wx.EVT_BUTTON, self.on_result_button)
        if isPass: button.Disable()
        return button

    def on_result_button(self, event):
        obj = event.GetEventObject()
        if obj.Name == "Pass":
            logger.debug("\"%s\" Result is : <Pass>" % self.name)
            self.set_result("Pass")
        else:
            logger.debug("\"%s\" Result is : <Pass>" % self.name)
            self.set_result("Fail")
        self.stop_test()

    def start_test(self):
        raise NotImplementedError

    def stop_test(self):
        raise NotImplementedError

    def set_result(self, result):
        uart = self.get_uart()
        uart.set_flag_result(flag=self.flag, result=result)
