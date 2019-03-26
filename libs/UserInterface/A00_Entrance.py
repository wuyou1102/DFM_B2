# -*- encoding:UTF-8 -*-

import logging
import sys

import wx

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"DFM V0.1", size=(400, 300),
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
        tool_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"工具"), wx.HORIZONTAL)
        test_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"测试"), wx.HORIZONTAL)

        PCBA = self.__create_button(label=u"PCBA", name=u"PCBA")
        Machine = self.__create_button(label=u"整机", name=u"Machine")
        RF = self.__create_button(label=u"射频", name=u"RF")
        WriteSN = self.__create_button(label=u"写号", name=u"WriteSN")

        tool_sizer.Add(WriteSN, 0, wx.EXPAND | wx.ALL, 5)
        test_sizer.Add(PCBA, 0, wx.EXPAND | wx.ALL, 5)
        test_sizer.Add(Machine, 0, wx.EXPAND | wx.ALL, 5)
        test_sizer.Add(RF, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(tool_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(test_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def __create_button(self, label, name):
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
        button.Bind(wx.EVT_BUTTON, self.__open_test)
        return button

    def __open_test(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "PCBA":
            from A01_CIT_PCBA import Frame
        elif name == "Machine":
            from A01_CIT_Machine import Frame
        elif name == "RF":
            from A01_CIT_RF import Frame
        elif name == "WriteSN":
            from A01_Write_Serial import Frame
        f = Frame()
        f.Show()
        self.parent.Close()
