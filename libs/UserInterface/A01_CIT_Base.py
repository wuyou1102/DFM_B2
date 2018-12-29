# -*- encoding:UTF-8 -*-

import logging
import sys
import wx
import TestPages

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=title, size=(800, 600))
        self.panel = Panel(self)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_0 = self.__init_horizontal_sizer_0()
        horizontal_1 = self.__init_horizontal_sizer_1()

        main_sizer.Add(horizontal_0, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(horizontal_1, 0, wx.EXPAND | wx.ALL, 0)

        self.SetSizer(main_sizer)
        self.Layout()

    def __init_horizontal_sizer_0(self):
        pass

    def __init_horizontal_sizer_1(self):
        pass
