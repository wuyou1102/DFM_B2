# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
from TestPages import Variable
from TestPages.Base import ReportPage
from TestPages.Base import RF_ConfigPage
from libs import Utility
from libs.Config import Color
from socket import timeout as SocketTimeout
from socket import error as SocketError

from libs.Utility import Socket

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self, title, type_, size=(800, 700), bandwidth="mix"):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=title, size=size)
        self.panel = Panel(self, type_=type_, bandwidth=bandwidth)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent, type_, bandwidth):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.bandwidth = bandwidth
        self.parent = parent
        self.type = type_
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # horizontal_0 = self.__init_horizontal_sizer_0()
        device_sizer = self.__init_device_sizer()
        test_sizer = self.__init_test_sizer()

        main_sizer.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(test_sizer, 1, wx.EXPAND | wx.ALL, 2)

        self.SetSizer(main_sizer)
        self.Layout()
        self.Enable(False)

    # def __init_horizontal_sizer_0(self):
    #     sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备信息"), wx.VERTICAL)
    #     sizer.Add(self.__init_port_sizer(), 0, wx.EXPAND | wx.ALL, 1)
    #     sizer.Add(self.__init_serial_number_sizer(), 0, wx.EXPAND | wx.ALL, 1)
    #     self.btn_get_info = wx.Button(self, wx.ID_ANY, u"刷新设备信息", wx.DefaultPosition, wx.DefaultSize, 0,
    #                                   name="get_info")
    #     self.btn_get_info.Bind(wx.EVT_BUTTON, self.on_button_click)
    #     sizer.Add(self.btn_get_info, 0, wx.EXPAND | wx.ALL, 1)
    #     return sizer

    def __init_device_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备信息"), wx.HORIZONTAL)
        sizer.Add(self.__init_serial_number_sizer(), 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.__init_button_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_button_sizer(self):
        size = (40, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        pic_connect = wx.Image('resource/icon/Connect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        pic_disconnect = wx.Image('resource/icon/Disconnect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        # pic_refresh = wx.Image('resource/icon/Refresh.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        self.btn_connect = wx.BitmapButton(self, wx.ID_ANY, pic_connect, wx.DefaultPosition, size, style=0,
                                           name='connect')
        self.btn_disconnect = wx.BitmapButton(self, wx.ID_ANY, pic_disconnect, wx.DefaultPosition, size, style=0,
                                              name='disconnect')

        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.btn_disconnect.Bind(wx.EVT_BUTTON, self.on_button_click)
        sizer.Add(self.btn_connect, 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.btn_disconnect, 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_serial_number_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                         wx.TE_READONLY | wx.TE_CENTER)
        f = wx.Font(23, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        title.SetFont(f)
        self.serial_number.SetFont(f)
        self.serial_number.SetBackgroundColour(Color.LightGray)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP | wx.LEFT, 5)
        sizer.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_test_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"测试"), wx.VERTICAL)
        self.test_view = ListBook(self, self.switch_cases())
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def switch_cases(self):
        if self.type == "PCBA":
            from libs.Config.Cases import PCBA_CASES
            return PCBA_CASES
        elif self.type == "MACHINE":
            from libs.Config.Cases import MACHINE_CASES
            return MACHINE_CASES
        elif self.type == "RF":
            if self.bandwidth == "2.4G":
                from libs.Config.Cases import RF_CASES_2400
                return RF_CASES_2400
            elif self.bandwidth == "5.8G":
                from libs.Config.Cases import RF_CASES_5800
                return RF_CASES_5800
            else:
                from libs.Config.Cases import RF_CASES
                return RF_CASES
        else:
            raise KeyError("Unknown type :\"%s\"" % self.type)

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "connect":
            self.connect()
        elif name == "disconnect":
            self.disconnect()
        elif name == "get_sn":
            self.update_serial_number()

    def connect(self):
        socket = self.get_variable("socket")
        if socket is not None:
            socket.close()
        try:
            socket = Socket.Client(address="192.168.1.1")
            self.set_variable(socket=socket)
            self.update_serial_number()
            Utility.append_thread(target=self.update_case_result, allow_dupl=False)
        except SocketError:
            Utility.Alert.Error(u"连接失败：超时。")
            return False
        except SocketTimeout:
            Utility.Alert.Error(u"连接失败：超时。")
            return False
        except IndexError:
            Utility.Alert.Error(u"连接失败：目标拒绝。")
        except KeyError:
            Utility.Alert.Error(u"设备没有有效的序列号，无法测试。请返回上一步完成写号后继续")
            self.clear_variable()
            socket.close()

    def disconnect(self, error_msg=None):
        self.test_view.clear_case_result()
        socket = Variable.get_socket()
        if socket is not None:
            socket.close()
        self.clear_variable()
        self.Layout()
        self.Enable(False)
        self.serial_number.SetValue("")
        if error_msg is not None:
            Utility.Alert.Error(error_msg)

    def update_serial_number(self):
        socket = Variable.get_socket()
        value = socket.get_serial_number()
        if value is None or value == "123456789012345678":
            raise KeyError
        else:
            self.serial_number.SetValue(value=value)

    def Enable(self, enable=True):
        lst1 = [self.btn_disconnect, self.test_view]
        lst2 = [self.btn_connect]
        for ctrl in lst1:
            ctrl.Enable(enable)
        for ctrl in lst2:
            ctrl.Enable(not enable)

    def update_case_result(self):
        self.test_view.clear_case_result()
        self.test_view.update_case_result()
        self.Enable()

    @staticmethod
    def set_variable(**kwargs):
        if 'socket' in kwargs.keys():
            Variable.set_socket(socket=kwargs['socket'])
        elif 'uart' in kwargs.keys():
            Variable.set_uart(uart=kwargs['uart'])

    @staticmethod
    def get_variable(key):
        if key == "uart":
            return Variable.get_uart()
        elif key == "socket":
            return Variable.get_socket()

    @staticmethod
    def clear_variable():
        Variable.set_uart()
        Variable.set_socket()

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
        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(right_sizer, 5, wx.EXPAND | wx.ALL, 0)
        self.__init_cases(cases=cases)
        self.SetSizer(main_sizer)
        self.Layout()

    def __init_cases(self, cases):
        for case in cases:
            c = case(self.__CaseView, type=self.parent.type)
            self.__ScrolledWindow.append(c)
            self.__CaseView.append(c)
        self.__add_report_page()
        if self.parent.type == "RF":
            self.__add_rf_config_page()
        self.__ScrolledWindow.refresh_scroll_window()

    def __add_report_page(self):
        page = ReportPage(self.__CaseView)
        self.__ScrolledWindow.append(page)
        self.__CaseView.append(page)

    def __add_rf_config_page(self):
        page = RF_ConfigPage(self.__CaseView)
        self.__ScrolledWindow.append(page)
        self.__CaseView.append(page)

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
        self.__ScrolledWindow = wx.ScrolledWindow(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(135, -1),
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
        socket = Variable.get_socket()
        results = socket.get_all_flag_results()
        if results is not None:
            for button in self.__buttons:
                try:
                    flag = button.get_flag()
                    result = results[flag - 1]
                    button.update_result(result=result)
                except AttributeError:
                    button.update_result()
        else:
            for button in self.__buttons:
                button.update_result()

    def clear_case_result(self):
        for button in self.__buttons:
            button.clear_result()

    def on_click(self, event):
        if self.__previous_select is not None: self.__previous_select.deselect()
        button = event.GetEventObject()
        self.__previous_select = button
        button.select()

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
            "True": Color.GoogleGreen,
            "False": Color.GoogleRed,
            "NotTest": Color.gray81,
            "Report": Color.GoogleYellow,
        }

    def __refresh_result(self):
        self.__result = self.__case.get_result()

    def __refresh_button(self):
        self.SetBackgroundColour(self.color)

    def update_result(self, result=None):
        if result is None:
            self.__refresh_result()
        else:
            if result in ["NotTest", "1"]:
                self.__result = "NotTest"
            elif result in ["True", "2"]:
                self.__result = "True"
            elif result in ["False", "3"]:
                self.__result = "False"
            else:
                self.__result = "NotTest"
                logger.error("Wrong Result Type: %s" % result)
        self.__refresh_button()

    def clear_result(self):
        self.__result = "NotTest"
        self.__refresh_button()

    def select(self, select=True):
        if select:
            self.SetBackgroundColour(Color.GoogleBlue)
            wx.CallAfter(self.__case.Show)
            # self.__case.Show()
        else:
            self.SetBackgroundColour(self.color)
            wx.CallAfter(self.__case.Hide)
            # self.__case.Hide()

    def deselect(self):
        self.SetBackgroundColour(self.color)
        wx.CallAfter(self.__case.Hide)
        # self.__case.Hide()

    @property
    def color(self):
        try:
            return self.__color[self.__result]
        except KeyError:
            return Color.White

    def get_flag(self):
        return self.__case.get_flag()


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
