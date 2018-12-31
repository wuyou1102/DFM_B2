# -*- encoding:UTF-8 -*-
import wx
import logging
from libs import Utility
from libs.Config import Color
from libs.Config import Font
import random

logger = logging.getLogger(__name__)


class Page(wx.Panel):
    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.name = name
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title =
        test_sizer = self.init_test_sizer()
        result_sizer = self.init_result_sizer()
        self.main_sizer.Add(test_sizer, 1, wx.EXPAND | wx.ALL, 1)
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

    def get_name(self):
        return self.name

    def get_result(self):
        return random.choice(["Pass", "Fail", "NotTest"])

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
        if isPass: button.Disable()
        return button

    def on_result_button(self, event):
        obj = event.GetEventObject()
        if obj.Name == "Pass":
            logger.debug("\"%s\" Result is : <Pass>" % self.name)
        else:
            logger.debug("\"%s\" Result is : <Pass>" % self.name)
