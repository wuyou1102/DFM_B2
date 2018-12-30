# -*- encoding:UTF-8 -*-
import wx
import logging

logger = logging.getLogger(__name__)
import random


class Page(wx.Panel):
    def __init__(self, parent, name, color=None):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.name = name
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, self.string(), wx.DefaultPosition, wx.DefaultSize, 0)
        main_sizer.Add(self.m_staticText1, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)
        self.Layout()

    def get_name(self):
        return self.name

    def get_result(self):
        return random.choice(["Pass", "Fail", "NotTest"])

    def string(self):
        aaa = ""
        for x in range(32):
            aaa += random.choice(list('qwertyuiopasdfhjk;lxzcm'))
        return aaa

    def Show(self):
        super(wx.Panel, self).Show()
        self.__parent.refresh()

    def Hide(self):
        super(wx.Panel, self).Hide()
        self.__parent.refresh()
