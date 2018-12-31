# -*- encoding:UTF-8 -*-
import logging
import sys

import wx

from libs import Utility
from libs.Config import Color

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')
from TestPages import MACHINE_CASES
from TestPages import PCBA_CASES


class Frame(wx.Frame):
    def __init__(self, title, _type):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=title, size=(800, 600))
        self.panel = Panel(self, _type=_type)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent, _type):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self._type = _type
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_0 = self.__init_horizontal_sizer_0()
        horizontal_1 = self.__init_horizontal_sizer_1()

        main_sizer.Add(horizontal_0, 1, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(horizontal_1, 3, wx.EXPAND | wx.ALL, 2)

        self.SetSizer(main_sizer)
        self.Layout()
        self.Enable(False)

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
        self.connect = wx.BitmapButton(self, wx.ID_ANY, pic_connect, wx.DefaultPosition, size, style=0, name='connect')
        self.disconnect = wx.BitmapButton(self, wx.ID_ANY, pic_disconnect, wx.DefaultPosition, size, style=0,
                                          name='disconnect')
        refresh.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.connect.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.disconnect.Bind(wx.EVT_BUTTON, self.on_button_click)
        port_sizer.Add(port_title, 0, wx.EXPAND | wx.TOP, 5)
        port_sizer.Add(self.port_choice, 1, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(refresh, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(self.connect, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(self.disconnect, 0, wx.EXPAND | wx.ALL, 1)
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
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"测试"), wx.VERTICAL)
        cases = PCBA_CASES if self._type == "PCBA" else MACHINE_CASES
        self.test_view = ListBook(self, cases)
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "refresh":
            self.port_choice.SetItems(Utility.Serial.list_ports())
        elif name == "connect":
            self.connect_uart()
        elif name == "disconnect":
            self.disconnect_uart()
        elif name == "set_sn":
            print 'set_sn'
        elif name == "get_sn":
            print 'get_sn'

    def connect_uart(self):
        print 'connect'
        if True:
            Utility.append_thread(target=self.update_case_result, allow_dupl=False)
        else:
            Utility.Alert.Error(u"无法打开设备")

    def disconnect_uart(self):
        print 'disconnect'
        self.test_view.clear_case_result()
        self.Layout()
        self.Enable(False)

    def Enable(self, enable=True):
        lst1 = [self.disconnect, self.button_sn, self.test_view]
        lst2 = [self.connect]
        for ctrl in lst1:
            ctrl.Enable(enable)
        for ctrl in lst2:
            ctrl.Enable(not enable)

    def update_case_result(self):
        self.test_view.update_case_result()
        self.Enable()


class ListBook(wx.Panel):
    def __init__(self, parent, cases):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.__case_pool = dict()
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__ScrolledWindow = ScrolledWindow(parent=self)
        self.__CaseView = CaseView(parent=self)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.__ScrolledWindow, 1, wx.EXPAND | wx.ALL, 0)
        right_sizer.Add(self.__CaseView, 1, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(left_sizer, 2, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(right_sizer, 7, wx.EXPAND | wx.ALL, 0)
        self.__init_cases(cases=cases)
        self.SetSizer(main_sizer)
        self.Layout()

    def __init_cases(self, cases):
        for case in cases:
            c = case(self.__CaseView)
            self.__ScrolledWindow.append(c)
            self.__CaseView.append(c)
        self.__ScrolledWindow.refresh_scroll_window()

    def update_case_result(self):
        self.__ScrolledWindow.update_case_result()

    def clear_case_result(self):
        self.__ScrolledWindow.clear_case_result()
        self.__ScrolledWindow.hide_last_select()


class ScrolledWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__case_pool = dict()
        self.__count = 0
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__container = wx.BoxSizer(wx.VERTICAL)
        self.__ScrolledWindow = wx.ScrolledWindow(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                                                  style=wx.VSCROLL)
        self.__ScrolledWindow.SetSizer(self.__container)
        self.__ScrolledWindow.SetScrollRate(5, 5)
        self.__ScrolledWindow.Layout()
        self.main_sizer.Fit(self.__ScrolledWindow)
        self.main_sizer.Add(self.__ScrolledWindow, 1, wx.EXPAND | wx.ALL, 0)
        self.__buttons = list()
        self.__previous_select = None
        self.SetSizer(self.main_sizer)
        self.Layout()

    def append(self, case):
        self.__append_in_case_pool(case)
        self.__append_in_scroll_window(case)
        self.__count += 1

    def __append_in_case_pool(self, case):
        self.__case_pool[self.__count] = case

    def __append_in_scroll_window(self, case):
        button = ScrollButton(self.__ScrolledWindow, case=case, index=self.__count)
        button.Bind(wx.EVT_BUTTON, self.on_click)
        self.__buttons.append(button)
        self.__container.Add(button, 0, wx.EXPAND | wx.ALL, 1)

    def refresh_scroll_window(self):
        self.__ScrolledWindow.SetSizer(self.__container, deleteOld=True)
        self.__ScrolledWindow.Scroll(0, 0)
        self.main_sizer.Layout()

    def update_case_result(self):
        for button in self.__buttons:
            button.update_result()

    def clear_case_result(self):
        for button in self.__buttons:
            button.clear_result()

    def on_click(self, event):
        if self.__previous_select is not None: self.__previous_select.deselect()
        button = event.GetEventObject()
        button.select()
        self.__previous_select = button

    def hide_last_select(self):
        self.__previous_select.deselect()


class ScrollButton(wx.Button):
    def __init__(self, parent, case, index):
        wx.Button.__init__(self, parent, wx.ID_ANY, case.get_name(), wx.DefaultPosition, (-1, 30),
                           style=wx.NO_BORDER)
        self.__case = case
        self.index = index
        self.__result = "NotTest"
        self.__color = {
            "Pass": Color.SpringGreen3,
            "Fail": Color.Red1,
            "NotTest": Color.gray81,
        }

    def __refresh_result(self):
        self.__result = self.__case.get_result()

    def __refresh_button(self):
        self.SetBackgroundColour(self.color)

    def update_result(self):
        self.__refresh_result()
        self.__refresh_button()

    def clear_result(self):
        self.__result = "NotTest"
        self.__refresh_button()

    def select(self, select=True):
        if select:
            self.SetBackgroundColour(Color.DodgerBlue3)
            self.__case.Show()
        else:
            self.SetBackgroundColour(self.color)
            self.__case.Hide()

    def deselect(self):
        self.SetBackgroundColour(self.color)
        self.__case.Hide()

    @property
    def color(self):
        return self.__color[self.__result]


class CaseView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__pages = list()
        self.SetSizer(self.panel_sizer)
        self.Layout()

    def append(self, page):
        self.panel_sizer.Add(page, 1, wx.EXPAND | wx.ALL, 0)
        page.Hide()

    def refresh(self):
        self.panel_sizer.Layout()
