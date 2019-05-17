# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
import time
import os
from TestPages.Base import ReportPage
import A01_CIT_Base
from libs import Utility
from libs.Config import Color
from libs.Config import Path
from TestPages import Variable
from libs.Utility.B2 import WebSever

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self, title, type_):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=title, size=(800, 600))
        self.panel = Panel(self, type_=type_)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(A01_CIT_Base.Panel):
    def __init__(self, parent, type_):
        A01_CIT_Base.Panel.__init__(self, parent=parent, type_=type_)

    def __init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.test_view = TestResult(parent=self, type_=self.type)
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

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


class TestResult(ReportPage):
    def __init__(self, parent, type_):
        ReportPage.__init__(self, parent=parent)
        self.type_ = type_

    def update_case_result(self):
        self.update_color_based_on_result()

    def clear_case_result(self):
        self.set_result_color_as_default()

    def init_title_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        return sizer

    def init_operation_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        upload = wx.Button(self, wx.ID_ANY, u"TODO:上传测试结果", wx.DefaultPosition, (-1, 40), 0, name="upload_result")
        refresh = wx.Button(self, wx.ID_ANY, u"刷新结果", wx.DefaultPosition, (-1, 40), 0, name="refresh_result")
        screenshots = wx.Button(self, wx.ID_ANY, u"保存截图", wx.DefaultPosition, (-1, 40), 0, name="screenshots")
        update_config = wx.Button(self, wx.ID_ANY, u"更新配置", wx.DefaultPosition, (-1, 40), 0, name="update_config")
        upload.Bind(wx.EVT_BUTTON, self.__on_button_click)
        refresh.Bind(wx.EVT_BUTTON, self.__on_button_click)
        screenshots.Bind(wx.EVT_BUTTON, self.__on_button_click)
        update_config.Bind(wx.EVT_BUTTON, self.__on_button_click)
        sizer.Add(upload, 0, wx.ALL, 5)
        sizer.Add(refresh, 0, wx.ALL, 5)
        sizer.Add(screenshots, 0, wx.ALL, 5)
        sizer.Add(update_config, 0, wx.ALL, 5)
        return sizer

    def __on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "refresh_result":
            Utility.append_thread(target=self.update_color_based_on_result)
        elif name == "upload_result":
            Utility.Alert.Info("Hello World!")
        elif name == "screenshots":
            self.capture_screen()
        elif name == "update_config":
            self.update_config()
        else:
            Utility.Alert.Error("Hello WUYOU!")

    def capture_screen(self):
        socket = Variable.get_socket()
        default_name = "%s.png" % socket.SerialNumber
        dlg = wx.FileDialog(self, "保存截图", "", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                            wildcard="Screenshots(*.png)|*.png|All files(*.*)|*.*",
                            defaultFile=default_name)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:  # 如果没有文件名后缀
                filename = filename + '.png'
        else:
            filename = None
        dlg.Destroy()
        time.sleep(1)
        if filename is not None:
            screen = wx.ScreenDC()
            size, pos = self.Parent.GetSize(), self.Parent.GetScreenPosition()
            width, height = size[0], size[1]
            x, y = pos[0], pos[1]
            bmp = wx.Bitmap(width, height)
            memory = wx.MemoryDC(bmp)
            memory.Blit(0, 0, width, height, screen, x, y)
            bmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)

    def update_config(self):
        socket = Variable.get_socket()
        dlg = UpdateDeviceConfigDialog(socket=socket, type_=self.type_)
        dlg.show_modal()


class UpdateDeviceConfigDialog(wx.Dialog):
    def __init__(self, socket, type_):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title="更新设备配置", size=(400, 300), pos=wx.DefaultPosition,
                           style=wx.CAPTION)
        self.panel = wx.Panel(self)
        self.type_ = type_
        self.web = WebSever("192.168.1.1")
        self.socket = socket
        self.result = ""
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.message = wx.TextCtrl(self.panel, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        main_sizer.Add(self.message, 1, wx.EXPAND | wx.ALL, 1)
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Layout()

    def show_modal(self):
        Utility.append_thread(self.modify_device_config)
        self.ShowModal()

    def get_result(self):
        return self.result

    def modify_device_config(self):
        try:
            if not self._start_web():
                self.result = "WebServer启动失败"
                return False
            if not self.__setup_config():
                self.result = "参数配置失败"
                return False
        finally:
            self.Destroy()

    def GetResult(self):
        return self.result

    def _start_web(self):
        if self.__start_web_server():
            time.sleep(2)
            for x in range(10):
                if self.__is_web_server_started():
                    self.output(u"WebServer启动成功")
                    return True
        self.output(u"WebServer启动失败，请手动进入配置模式后重试。")
        return False

    def __start_web_server(self):
        self.output(u"正在尝试启动WebServer")
        return self.socket.start_web_server()

    def __is_web_server_started(self):
        self.output(u"正在检查WebServer是否已经启动")
        return self.web.isStart()

    def __setup_config(self):
        print self.type_
        if self.type_ == "Omni":
            if self.web.SetAsBS(NW_ID=168, TYF=13):
                self.output(u"修改配置成功")
                return True
        elif self.type_ == "Dire":
            if self.web.SetAsND(NW_ID=168, NW_NUM=1, USR_ID=0):
                self.output(u"修改配置成功")
                return True
        self.output(u"修改配置失败")
        return False

    def __reboot(self):
        for x in range(3):
            self.output(u"正在自动重启设备")
            self.web.RebootDevice()
            time.sleep(2)
            if not Utility.is_device_connected(address="192.168.1.1", port=51341):
                self.output(u"自动重启成功")
                return True
        self.output(u"自动重启失败，请手动重启")
        return False

    def output(self, msg):
        msg = "%s: %s\n" % (Utility.get_timestamp('%H:%M:%S'), msg)
        wx.CallAfter(self.message.AppendText, msg)
        time.sleep(0.005)
