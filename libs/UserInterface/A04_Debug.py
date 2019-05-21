# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
import A01_CIT_Base
from libs.Config import Color

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"调试工具", size=(800, 600))
        self.panel = Panel(self)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(A01_CIT_Base.Panel):
    def __init__(self, parent):
        A01_CIT_Base.Panel.__init__(self, parent=parent, type_="")

    def __init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.test_view = DebugPanel(parent=self)
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer


class DebugPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.__init_row_sizer1(), 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.__init_row_sizer2(), 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def __init_row_sizer1(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.create_button(u"加载协议栈", "load_protocol_stack"), 0, wx.ALL, 1)
        sizer.Add(self.create_button(u"不加载协议栈", "unload_protocol_stack"), 0, wx.ALL, 1)
        sizer.Add(self.create_button(u"设置TX模式", "set_tx_mode_20m"), 0, wx.ALL, 1)
        sizer.Add(self.create_button(u"设置RX模式", "set_rx_mode_20m"), 0, wx.ALL, 1)
        sizer.Add(self.create_button(u"开启基带", "release_baseband"), 0, wx.ALL, 1)
        sizer.Add(self.create_button(u"关闭基带", "hold_baseband"), 0, wx.ALL, 1)
        return sizer

    def __init_row_sizer2(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__init_freq_sizer(), 0, wx.ALL, 1)

        return sizer

    def get_device(self):
        return self.parent.get_variable("socket")

    def clear_case_result(self):
        self.refresh_freq_point(clear=True)

    def update_case_result(self):
        self.refresh_freq_point(clear=False)

    def __init_freq_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                         wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.current_point.Bind(wx.EVT_TEXT_ENTER, self.set_freq_point)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def refresh_freq_point(self, clear=False):
        if clear:
            self.current_point.SetValue("")
        else:
            device = self.get_device()
            value = device.get_frequency_point()
            self.current_point.SetValue(value[:-2])

    def set_freq_point(self, event):
        device = self.get_device()
        device.set_frequency_point(self.current_point.GetValue() + '000')
        self.refresh_freq_point(clear=False)

    def create_button(self, label, name):
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
        button.Bind(wx.EVT_BUTTON, self.on_button_click)
        return button

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        device = self.get_device()
        func = device.__getattribute__(name)
        func()
