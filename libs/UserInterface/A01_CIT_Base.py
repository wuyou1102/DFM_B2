# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
from libs import Utility
from libs.Config import Color

from libs.Utility.UART import UART
from TestPages import Variable
from TestPages.Base import Report
import serial

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self, title, type, size=(800, 600)):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=title, size=size)
        self.panel = Panel(self, type=type)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent, type):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.type = type
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_0 = self.__init_horizontal_sizer_0()
        horizontal_1 = self.__init_horizontal_sizer_1()

        main_sizer.Add(horizontal_0, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(horizontal_1, 1, wx.EXPAND | wx.ALL, 2)

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
        self.btn_refresh = wx.BitmapButton(self, wx.ID_ANY, pic_refresh, wx.DefaultPosition, size, style=0,
                                           name='refresh')
        self.btn_connect = wx.BitmapButton(self, wx.ID_ANY, pic_connect, wx.DefaultPosition, size, style=0,
                                           name='connect')
        self.btn_disconnect = wx.BitmapButton(self, wx.ID_ANY, pic_disconnect, wx.DefaultPosition, size, style=0,
                                              name='disconnect')
        self.btn_refresh.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.btn_disconnect.Bind(wx.EVT_BUTTON, self.on_button_click)
        port_sizer.Add(port_title, 0, wx.EXPAND | wx.TOP, 5)
        port_sizer.Add(self.port_choice, 1, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(self.btn_refresh, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(self.btn_connect, 0, wx.EXPAND | wx.ALL, 1)
        port_sizer.Add(self.btn_disconnect, 0, wx.EXPAND | wx.ALL, 1)
        return port_sizer

    def __init_serial_number_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.button_sn = wx.Button(self, wx.ID_ANY, u"写", wx.DefaultPosition, (25, 25), 0, name="set_sn")
        self.button_sn.Bind(wx.EVT_BUTTON, self.on_button_click)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.button_sn, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)

        return sizer

    def __init_horizontal_sizer_1(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"测试"), wx.VERTICAL)
        self.test_view = ListBook(self, self.switch_cases())
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def switch_cases(self):
        if self.type == "PCBA":
            from TestPages import PCBA_CASES
            return PCBA_CASES
        elif self.type == "MACHINE":
            from TestPages import MACHINE_CASES
            return MACHINE_CASES
        elif self.type == "RF":
            from TestPages import RF_CASES
            return RF_CASES
        else:
            raise KeyError("Unknown type :\"%s\"" % self.type)

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "refresh":
            self.port_choice.SetItems(UART.list_ports())
        elif name == "connect":
            self.connect()
        elif name == "disconnect":
            self.disconnect()
        elif name == "set_sn":
            self.set_serial_number_via_uart()
        elif name == "get_sn":
            self.update_serial_number()

    def connect(self):
        port = self.get_selected_port()
        if port is False: return False
        try:
            uart = UART(port=port)
        except serial.serialutil.SerialException as e:
            Utility.Alert.Error(e.message)
            return False
        if uart.is_uart_connected():
            self.set_variable(uart=uart)
            self.update_serial_number()
            Utility.append_thread(target=self.update_case_result, allow_dupl=False)
        else:
            Utility.Alert.Error(u"无法打开设备")

    def disconnect(self):
        self.test_view.clear_case_result()
        uart = Variable.get_uart()
        if uart is not None:
            uart.close()
        self.clear_variable()
        self.Layout()
        self.Enable(False)

    def set_serial_number_via_uart(self):
        serial = self.serial_number.GetValue()
        if not serial:
            Utility.Alert.Error(u"请输入正确的序列号")
            return False
        else:
            uart = Variable.get_uart()
            return uart.set_serial_number(serial)

    def update_serial_number(self):
        uart = Variable.get_uart()
        self.serial_number.SetValue(value=uart.SerialNumber)

    def Enable(self, enable=True):
        lst1 = [self.btn_disconnect, self.button_sn, self.test_view]
        lst2 = [self.btn_connect, self.port_choice, self.btn_refresh]
        for ctrl in lst1:
            ctrl.Enable(enable)
        for ctrl in lst2:
            ctrl.Enable(not enable)

    def update_case_result(self):
        self.test_view.update_case_result()
        self.Enable()

    @staticmethod
    def set_variable(**kwargs):
        Variable.set_uart(uart=kwargs['uart'])

    @staticmethod
    def clear_variable():
        Variable.set_uart()

    def get_selected_port(self):
        selected = self.port_choice.GetStringSelection()
        if selected:
            return selected
        else:
            Utility.Alert.Error(u"请选择端口号")
            return False

    def get_type(self):
        return self._type


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
        main_sizer.Add(left_sizer, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 0)
        self.__init_cases(cases=cases)
        self.SetSizer(main_sizer)
        self.Layout()

    def __init_cases(self, cases):
        for case in cases:
            c = case(self.__CaseView, type=self.parent.type)
            self.__ScrolledWindow.append(c)
            self.__CaseView.append(c)
        self.__add_report_page()
        self.__ScrolledWindow.refresh_scroll_window()

    def __add_report_page(self):
        report = Report(self.__CaseView)
        self.__ScrolledWindow.append(report)
        self.__CaseView.append(report)

    def update_case_result(self):
        self.__ScrolledWindow.update_case_result()

    def clear_case_result(self):
        self.__ScrolledWindow.clear_case_result()
        self.__ScrolledWindow.hide_last_select()

    def next_page(self):
        self.__ScrolledWindow.next_page()


class ScrolledWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__case_pool = dict()
        self.__count = 0
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__container = wx.BoxSizer(wx.VERTICAL)
        self.__ScrolledWindow = wx.ScrolledWindow(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(100, -1),
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
        if self.__previous_select is not None:
            self.__previous_select.deselect()

    def next_page(self):
        self.__previous_select.deselect()
        self.__previous_select.update_result()
        index = self.__previous_select.index
        if index <= len(self.__case_pool):
            button = self.__buttons[index + 1]
            button.select()
            self.__previous_select = button


class ScrollButton(wx.Button):
    def __init__(self, parent, case, index):
        wx.Button.__init__(self, parent, wx.ID_ANY, case.get_name(), wx.DefaultPosition, (-1, 30),
                           style=wx.NO_BORDER)
        self.__case = case
        self.index = index
        self.__result = "NotTest"
        self.__color = {
            "True": Color.SpringGreen3,
            "False": Color.Red1,
            "NotTest": Color.gray81,
            "Report": Color.Yellow
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
        self.__parent = parent
        self.__pages = list()
        self.SetSizer(self.panel_sizer)
        self.Layout()

    def append(self, page):
        self.panel_sizer.Add(page, 1, wx.EXPAND | wx.ALL, 0)
        page.Hide()

    def refresh(self):
        self.panel_sizer.Layout()

    def next_page(self):
        self.__parent.next_page()
