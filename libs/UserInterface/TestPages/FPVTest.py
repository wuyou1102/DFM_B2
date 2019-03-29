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

logger = logging.getLogger(__name__)


class FPV(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.preview = None

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

        self.btn_config = create_button(label=u"修改配置", name="config")
        self.btn_start = create_button(label=u"开始测试", name="start")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btn_config, 0, wx.EXPAND, 1)
        sizer.Add(self.btn_start, 0, wx.EXPAND, 1)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "config":
            dlg = ConfigDialog()
            dlg.ShowModal()

    def play(self):
        socket = self.get_communicat()

        print self.preview.GetScreenPosition()
        print self.preview.GetSize()
        # print self.GetScreenPosition()

        while True:
            self.preview.play()
            result = socket.get_rssi_and_bler()
            bler = int(result[8:], 16)
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            self.rssi_0.SetValue(str(rssi0))
            self.rssi_1.SetValue(str(rssi1))
            self.bler.SetValue(str(bler))
            self.Sleep(1)

    def before_test(self):
        super(FPV, self).before_test()
        # Utility.append_thread(self.is_active)
        if self.preview is None:
            self.preview = PreviewDialog()
        self.preview.SetPosition(self.GetParentPosition())
        self.preview.Show()
        self.SetFocus()

    def GetParentPosition(self):
        x, y = self.Parent.Parent.Parent.Parent.GetPosition()
        w, h = self.Parent.Parent.Parent.Parent.GetSize()
        return (x + w + 4, y + 4)

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        if self.preview is not None and self.preview.IsShown():
            self.preview.Hide()

    @staticmethod
    def GetName():
        return u"图传测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.FPV_MACHINE


class PreviewDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title=u"预览", size=(640, 360),
                           pos=wx.DefaultPosition, style=wx.STAY_ON_TOP | wx.CAPTION | wx.MINIMIZE_BOX | wx.SYSTEM_MENU)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.BLACK)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(main_sizer)
        self.Layout()

        self.__player = vlc.Instance().media_player_new()
        self.__player.set_hwnd(self.GetHandle())
        self.reset_media()

    def play(self):
        print self.__player.get_state()
        if self.__player.get_state() != vlc.State.Playing:
            self.__player.play()

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
        cancel = wx.Button(self.panel, wx.ID_ANY, u"取消", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        save = wx.Button(self.panel, wx.ID_ANY, u"保存", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
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
        self.Destroy()

    def on_cancel(self, event):
        self.Destroy()
