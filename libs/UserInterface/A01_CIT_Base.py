# -*- encoding:UTF-8 -*-
import logging
import sys

import wx

from libs import Utility

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

        main_sizer.Add(horizontal_0, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(horizontal_1, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def __init_horizontal_sizer_0(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备信息"), wx.VERTICAL)
        sizer.Add(self.__init_port_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.__init_serial_number_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_port_sizer(self):
        size = (25, 25)
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_title = wx.StaticText(self, wx.ID_ANY, u"端口号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.port_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, Utility.Serial.list_ports(),
                                     0)
        pic_refresh = wx.Image('resource/icon/Refresh.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        pic_connect = wx.Image('resource/icon/Connect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        pic_disconnect = wx.Image('resource/icon/Disconnect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        refresh = wx.BitmapButton(self, wx.ID_ANY, pic_refresh, wx.DefaultPosition, size, style=0, name='refresh')
        connect = wx.BitmapButton(self, wx.ID_ANY, pic_connect, wx.DefaultPosition, size, style=0, name='connect')
        disconnect = wx.BitmapButton(self, wx.ID_ANY, pic_disconnect, wx.DefaultPosition, size, style=0,
                                     name='disconnect')
        refresh.Bind(wx.EVT_BUTTON, self.on_button_click)
        connect.Bind(wx.EVT_BUTTON, self.on_button_click)
        disconnect.Bind(wx.EVT_BUTTON, self.on_button_click)
        port_sizer.Add(port_title, 0, wx.EXPAND | wx.TOP, 5)
        port_sizer.Add(self.port_choice, 1, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(refresh, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(connect, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(disconnect, 0, wx.EXPAND | wx.ALL, 1)
        return port_sizer

    def __init_serial_number_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.button_sn = wx.Button(self, wx.ID_ANY, u"写", wx.DefaultPosition, (25, 25), 0, name="set_sn")
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.button_sn, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)

        return sizer

    def __init_horizontal_sizer_1(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "refresh":
            self.port_choice.SetItems(Utility.Serial.list_ports())
        elif name == "connect":
            print 'connect'
        elif name == "disconnect":
            print 'disconnect'
        elif name == "set_sn":
            print 'set_sn'
        elif name == "get_sn":
            print 'get_sn'
