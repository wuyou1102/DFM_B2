# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import Path
from libs import Utility
import vlc
from libs.Config import String
import time
from libs.Utility.B2 import WebSever
from libs.Utility import Timeout

logger = logging.getLogger(__name__)


class FLAG(object):
    STOP = False


def step(func):
    def wrapper(*args, **kwargs):
        if FLAG.STOP:
            raise StopIteration
        return func(*args, **kwargs)

    return wrapper


class FPV(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.stop_flag = False
        self.target = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp', option='address')
        self.__player = vlc.Instance().media_player_new()
        self.__player.set_hwnd(self.panel.GetHandle())
        self.reset_media()

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
        rssi_sizer.Add(self.__init_button_sizer(), 0, wx.ALL, 1)
        return rssi_sizer

    def __init_previewer_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.BLACK)
        sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_button_sizer(self):
        def create_button(label, name):
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
            button.Bind(wx.EVT_BUTTON, self.on_button_click)
            return button

        self.btn_config = create_button(label=u"修改文件配置", name="config")
        self.btn_start = create_button(label=u"将配置更新到设备中", name="update")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btn_config, 0, wx.EXPAND, 1)
        sizer.Add(self.btn_start, 0, wx.EXPAND, 1)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "config":
            dlg = ConfigDialog()
            if dlg.ShowModal() == wx.ID_OK:
                self.target = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp', option='address')
                self.reset_media()
            dlg.Destroy()
        if name == "update":
            self.update_device_config()

    def before_test(self):
        self.stop_flag = False

    def start_test(self):
        Utility.append_thread(self.check_device_is_connect)
        Utility.append_thread(self.update_info)

    def update_device_config(self):
        socket = self.get_communicat()
        pass

    def check_device_is_connect(self):
        while not self.stop_flag:
            if Utility.is_device_started(address=self.target, timeout=1000):
                self.play()
            else:
                self.stop()

    def update_info(self):
        socket = self.get_communicat()
        while not self.stop_flag:
            print self.__player.get_state()
            result = socket.get_rssi_and_bler()
            bler = int(result[8:], 16)
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            wx.CallAfter(self.rssi_0.SetValue, str(rssi0))
            wx.CallAfter(self.rssi_1.SetValue, str(rssi1))
            wx.CallAfter(self.bler.SetValue, str(bler))
            self.Sleep(1)

    def stop_test(self):
        self.stop_flag = True
        self.stop()

    @staticmethod
    def GetName():
        return u"图传测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.FPV_MACHINE

    def play(self):
        if self.__player.get_state() not in [vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering]:
            logger.debug("Start the vlc play.")
            self.__player.play()

    def pause(self):
        if self.__player.get_state() in [vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering]:
            logger.debug("Pause the vlc play.")
            self.__player.pause()

    def stop(self):
        if self.__player.get_state() != vlc.State.Stopped:
            self.__player.stop()

    def reset_media(self):
        while self.__player.get_state() != vlc.State.Stopped:
            self.__player.stop()
            time.sleep(0.2)
        media = self.__player.get_instance().media_new(self.get_rtsp_media())
        self.__player.set_media(media)

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
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title="重启中", size=(250, 200), pos=wx.DefaultPosition)
        self.panel = wx.Panel(self)
        self.web = WebSever("192.168.1.1")
        self.socket = socket
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Layout()

    def __reboot_device(self):
        for x in range(120):
            if self.is_device_started():
                break
            time.sleep(0.5)
        self.Destroy()

    @step
    def is_device_started(self):
        return Utility.is_device_started()

    def ShowM(self):
        self.modify_device_config()
        self.ShowModal()

    def modify_device_config(self):
        if self._start_web():
            self.output(u"WebServer启动成功")
        else:
            self.output(u"WebServer启动失败，请手动进入配置模式后重试。")
            return False
        if not self.__setup_config():
            return False
        self.__reboot()

    def _start_web(self):
        if self.__is_web_server_started():
            return True
        if self.__start_web_server():
            time.sleep(2)
            for x in range(10):
                if self.__is_web_server_started():
                    return True
        return False

    @step
    def __start_web_server(self):
        self.output(u"正在尝试启动WebServer")
        return self.socket.start_web_server()

    @step
    def __is_web_server_started(self):
        self.output(u"正在检查WebServer是否已经启动")
        return self.web.isStart()

    @step
    def __setup_config(self):
        network_id = Utility.ParseConfig.get(path=Path.CONFIG, section='rtsp', option='id')
        logger.debug("I got network id : %s" % network_id)
        self.output(u"正在修改设备配置")
        if self.web.SetAsBS(NW_ID=int(network_id), TYF=4):
            self.output(u"修改配置成功")
            return True
        self.output(u"修改配置失败")
        return False

    @step
    def __reboot(self):
        self.web.RebootDevice()

    def output(self, msg):
        msg = "%s: %s\n" % (Utility.get_timestamp(), msg)
        wx.CallAfter(self.message.AppendText, msg)
        self.Sleep(0.005)
