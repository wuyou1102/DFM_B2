# -*- encoding:UTF-8 -*-

import logging
import sys

import wx

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"DFM V0.1", size=(250, 200),
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.panel = Panel(self)

    def Close(self):
        self.Destroy()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        PCBA = wx.Button(self, wx.ID_ANY, u"PCBA测试", wx.DefaultPosition, wx.DefaultSize, 0, name=u"PCBA")
        Machine = wx.Button(self, wx.ID_ANY, u"整机测试", wx.DefaultPosition, wx.DefaultSize, 0, name=u"Machine")
        RF = wx.Button(self, wx.ID_ANY, u"射频测试", wx.DefaultPosition, wx.DefaultSize, 0, name=u"RF")
        PCBA.Bind(wx.EVT_BUTTON, self.open_test)
        Machine.Bind(wx.EVT_BUTTON, self.open_test)
        RF.Bind(wx.EVT_BUTTON, self.open_test)

        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(PCBA, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        button_sizer.Add(Machine, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        button_sizer.Add(RF, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(button_sizer, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 15)

        self.SetSizer(main_sizer)
        self.Layout()

    def open_test(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "PCBA":
            from A01_CIT_PCBA import Frame
        elif name == "Machine":
            from A01_CIT_Machine import Frame
        elif name == "RF":
            from A02_RF_Frame import Frame
        f = Frame()
        f.Show()
        self.parent.Close()
