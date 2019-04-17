# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import Path
from libs import Utility
from libs.Config import String
import time
from libs.Utility.B2 import WebSever
from libs.Utility import Timeout
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

COUNTDOWN = 60
COUNTDOWN_STRING = u"倒计时："


def Image2Bitmap(Image):
    width, height = Image.size
    buff = Image.convert('RGB').tobytes()
    return wx.Bitmap.FromBuffer(width, height, buff)


class FPV(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.config = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp')
        self.stop_flag = False
        self.update_info_timer = wx.Timer(self)
        self.countdown_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_info, self.update_info_timer)
        self.Bind(wx.EVT_TIMER, self.countdown_info, self.countdown_timer)

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_info_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.__init_previewer_sizer(), 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_info_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__init_rssi_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_rssi_sizer(self):
        def init_rssi(label):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0)
            value = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1),
                                wx.TE_READONLY | wx.TE_CENTRE)
            value.SetBackgroundColour(Color.LightGray)
            sizer.Add(title, 0, wx.TOP, 5)
            sizer.Add(value, 0, wx.ALL, 1)
            return sizer, value

        rssi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer0, self.rssi_0 = init_rssi(u"天线 0: ")
        sizer1, self.rssi_1 = init_rssi(u"天线 1: ")
        sizer2, self.bler = init_rssi(u"误块数: ")
        rssi_sizer.Add(sizer0, 0, wx.ALL, 1)
        rssi_sizer.Add(sizer1, 0, wx.ALL, 1)
        rssi_sizer.Add(sizer2, 0, wx.ALL, 1)
        rssi_sizer.Add(self.__init_button_sizer(), 1, wx.ALL, 1)
        rssi_sizer.Add(self.__init_countdown_sizer(), 0, wx.ALL, 1)
        return rssi_sizer

    def __init_previewer_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.preview = PreviewPanel(parent=self)
        sizer.Add(self.preview, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_button_sizer(self):
        def create_button(label, name):
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
            button.Bind(wx.EVT_BUTTON, self.on_button_click)
            return button

        self.btn_config = create_button(label=u"修改配置文件", name="config")
        self.btn_start = create_button(label=u"将配置更新到设备中", name="update")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btn_config, 0, wx.EXPAND, 1)
        sizer.Add(self.btn_start, 0, wx.EXPAND, 1)
        return sizer

    def __init_countdown_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.wx_countdown = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.wx_countdown.SetFont(Font.NORMAL_20)
        sizer.Add(self.wx_countdown, 0, wx.LEFT, 10)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "config":
            dlg = ConfigDialog()
            if dlg.ShowModal() == wx.ID_OK:
                self.config = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp')
                Utility.Alert.Warn(u"重启测试已使配置生效")
            dlg.Destroy()
        if name == "update":
            self.update_device_config()

    def before_test(self):
        super(FPV, self).before_test()
        self.preview.Reset()

    def update_device_config(self):
        self.stop_test()
        socket = self.get_communicate()
        dlg = UpdateDeviceConfigDialog(socket=socket)
        dlg.show_modal()
        if dlg.get_result():
            Utility.Alert.Error(u"更新设备配置失败，失败项:\"%s\"" % dlg.get_result())
        if socket.reconnect():
            self.start_test()
        else:
            self.Parent.Parent.Parent.disconnect()

    def set_as_connect(self):
        wx.CallAfter(self.wx_countdown.SetLabel, u"已检测到连接")
        wx.CallAfter(self.wx_countdown.SetForegroundColour, Color.GoogleGreen)
        self.EnablePass(enable=True)

    def refresh_preview(self, ipc):
        while not self.stop_flag:
            retval, image = ipc.GetFrame(tuple(self.preview.GetSize()))
            self.preview.SetBitmap(Image2Bitmap(image))
            self.preview.UpdateBitmap()
            if retval:
                time.sleep(0.015)
            else:
                break

    def update_info(self, event):
        socket = self.get_communicate()
        result = socket.get_rssi_and_bler()
        if result is None:
            self.stop_test()
            if socket.reconnect():
                self.start_test()
            else:
                self.Parent.Parent.Parent.disconnect(error_msg=u"连接异常，请手动尝试重新连接")
            return
        if result != "0000000000000000":
            bler = int(result[8:], 16)
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            wx.CallAfter(self.rssi_0.SetValue, str(rssi0))
            wx.CallAfter(self.rssi_1.SetValue, str(rssi1))
            wx.CallAfter(self.bler.SetValue, str(bler))

    def countdown_info(self, event):
        label = self.wx_countdown.GetLabel()
        if COUNTDOWN_STRING in label:
            value = int(label.replace(COUNTDOWN_STRING, ""))
            if value == 0:
                self.wx_countdown.SetLabel(u"未检测到连接，请点击Fail")
                self.wx_countdown.SetForegroundColour(Color.GoogleRed)
                self.countdown_timer.Stop()
            else:
                self.wx_countdown.SetLabel(COUNTDOWN_STRING + str(value - 1))
        else:
            self.countdown_timer.Stop()

    def check_rtsp_server(self):
        while not self.stop_flag:
            if Utility.is_device_connected(address=self.config.get('address'), port=self.config.get('port'),
                                           timeout=0.5):
                self.set_as_connect()
                ipc = IpCamera(self.get_rtsp_media())
                if ipc.isOpened():
                    self.refresh_preview(ipc=ipc)
        try:
            del ipc
        except UnboundLocalError:
            pass
        logger.debug("FPV RTSP SERVER IS CONNECTED OVER")

    def StartTimer(self):
        self.wx_countdown.SetLabel(COUNTDOWN_STRING + str(COUNTDOWN))
        self.wx_countdown.SetForegroundColour(Color.Black)
        self.update_info_timer.Start(1001)
        self.countdown_timer.Start(1003)

    def StopTimer(self):
        self.update_info_timer.Stop()
        self.countdown_timer.Stop()

    def start_test(self):
        def _start_test():
            time.sleep(1.1)
            self.test_thread = Utility.append_thread(self.check_rtsp_server)

        self.stop_flag = False
        self.StartTimer()
        Utility.append_thread(target=_start_test)

    def stop_test(self):
        self.StopTimer()
        self.stop_flag = True

    @staticmethod
    def GetName():
        return u"图传测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.FPV_MACH

    @staticmethod
    def get_rtsp_media():
        config = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp')
        address = config.get("address", "192.168.90.48")
        port = config.get("port", "554")
        username = config.get("username", "admin")
        password = config.get("password", "Password01!")
        return "rtsp://{username}:{password}@{address}:{port}".format(
            username=username,
            password=password,
            port=port,
            address=address
        )


class IpCamera(object):
    def __init__(self, url):
        self.video = cv2.VideoCapture(url)

    def isOpened(self):
        return self.video.isOpened()

    def GetFrame(self, size):
        try:
            frame = self.__get_frame(size=size)
            return True, frame
        except Timeout.Timeout:
            return False, Image.new("RGB", size, color='black')
        except IndexError:
            return False, Image.new("RGB", size, color='black')

    @Timeout.timeout(0.5)
    def __get_frame(self, size):
        retval, image = self.video.read()
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize(size=size)


class PreviewPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.bitmap = Image2Bitmap(Image.new("RGB", tuple(self.GetSize()), color='black'))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateBitmap(self):
        self.Refresh()
        self.Update()

    def SetBitmap(self, bitmap):
        self.bitmap = bitmap

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self.bitmap, 0, 0)

    def Reset(self):
        self.SetBitmap(Image2Bitmap(Image.new("RGB", tuple(self.GetSize()), color='black')))
        self.UpdateBitmap()


class ConfigDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title="修改配置", size=(250, 200), pos=wx.DefaultPosition)
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        config_sizer = self.__init_config_sizer()
        button_sizer = self.__init_button_sizer()
        main_sizer.Add(config_sizer, 0, wx.ALIGN_CENTRE | wx.ALL, 3)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTRE | wx.ALL, 3)
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Layout()

    def __init_config_sizer(self, name="rtsp"):
        def create_text_ctrl(title, value):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(self.panel, wx.ID_ANY, title, wx.DefaultPosition, wx.DefaultSize, 0)
            title.SetFont(Font.COMMON_1)
            value = wx.TextCtrl(self.panel, wx.ID_ANY, value, wx.DefaultPosition, wx.DefaultSize, 0)
            value.SetFont(Font.COMMON_1)
            sizer.Add(title, 0, wx.EXPAND | wx.TOP, 5)
            sizer.Add(value, 1, wx.EXPAND | wx.ALL, 1)
            return sizer, value

        sizer = wx.BoxSizer(wx.VERTICAL)
        config = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp')
        address_sizer, self.address = create_text_ctrl("地  址: ", config.get("address", "192.168.90.48"))
        port_sizer, self.port = create_text_ctrl("端口号: ", config.get("port", "554"))
        username_sizer, self.username = create_text_ctrl("用户名: ", config.get("username", "admin"))
        password_sizer, self.password = create_text_ctrl("密  码: ", config.get("password", "Password01!"))
        network_id_sizer, self.network_id = create_text_ctrl("网络ID: ", config.get("id", "666"))
        sizer.Add(address_sizer, 0, wx.EXPAND, 1)
        sizer.Add(port_sizer, 0, wx.EXPAND, 1)
        sizer.Add(username_sizer, 0, wx.EXPAND, 1)
        sizer.Add(password_sizer, 0, wx.EXPAND, 1)
        sizer.Add(network_id_sizer, 0, wx.EXPAND, 1)
        return sizer

    def __init_button_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel = wx.Button(self.panel, wx.ID_CANCEL, u"取消", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        save = wx.Button(self.panel, wx.ID_OK, u"保存", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        save.Bind(wx.EVT_BUTTON, self.on_save)
        sizer.Add(save, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(cancel, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def on_save(self, event):
        data = dict()
        data["address"] = self.address.GetValue()
        data["port"] = self.port.GetValue()
        data["username"] = self.username.GetValue()
        data["password"] = self.password.GetValue()
        data["id"] = self.network_id.GetValue()
        Utility.ParseConfig.modify(path=Path.CONFIG, data={"rtsp": data})
        event.Skip()


class UpdateDeviceConfigDialog(wx.Dialog):
    def __init__(self, socket):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title="更新设备配置", size=(400, 300), pos=wx.DefaultPosition,
                           style=wx.CAPTION)
        self.panel = wx.Panel(self)
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
            if not self.__reboot():
                self.__wait_for_reboot()
            if not self.__wait_for_boot_up():
                self.result = "启动检测失败"
                return False
            return True
        finally:
            self.EndModal(wx.OK)

    def GetResult(self):
        return self.result

    def __wait_for_boot_up(self, timeout=100):
        for x in range(timeout):
            self.output(u"检查设备是否已经启动[%s]" % (x + 1))
            if Utility.is_device_connected(address="192.168.1.1", port=51341):
                self.output(u"启动成功")
                return True
        self.output(u"启动失败")
        return False

    def __wait_for_reboot(self):
        while True:
            if Utility.is_device_connected(address="192.168.1.1", port=51341):
                self.output(u"重启失败，请手动重启")
            else:
                self.output(u"检测到重启")
                break
            time.sleep(1)

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
        network_id = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp', option='id')
        logger.debug("I got network id : %s" % network_id)
        self.output(u"正在修改设备配置")
        if self.web.SetAsBS(NW_ID=int(network_id), TYF=4):
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
