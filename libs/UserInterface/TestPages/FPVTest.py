# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs.Config import Path
from libs import Utility
import vlc

logger = logging.getLogger(__name__)


class FPVTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"图传测试", flag="FPV")
        self.player = Player(self.on_result_button)

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        address_sizer = self.__init_rtsp_sizer()

        sizer.Add(address_sizer, 0, wx.EXPAND | wx.ALL, 0)

        return sizer

    def __init_rtsp_sizer(self, name="rtsp"):
        def create_text_ctrl(title, value):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(self, wx.ID_ANY, title, wx.DefaultPosition, wx.DefaultSize, 0)
            title.SetFont(Font.COMMON_1)
            value = wx.TextCtrl(self, wx.ID_ANY, value, wx.DefaultPosition, wx.DefaultSize, 0)
            value.SetFont(Font.COMMON_1)
            sizer.Add(title, 0, wx.EXPAND | wx.TOP, 4)
            sizer.Add(value, 1, wx.EXPAND | wx.ALL, 1)
            return sizer, value
        rtsp_sizer = wx.BoxSizer(wx.VERTICAL)
        config = self.__get_config(name=name)
        address_sizer, self.address = create_text_ctrl("地  址: ", config.get("address", "192.168.90.48"))
        port_sizer, self.port = create_text_ctrl("端口号: ", config.get("port", "554"))
        username_sizer, self.username = create_text_ctrl("用户名: ", config.get("username", "admin"))
        password_sizer, self.password = create_text_ctrl("密  码: ", config.get("password", "Password01!"))
        rtsp_sizer.Add(address_sizer, 0, wx.EXPAND, 1)
        rtsp_sizer.Add(port_sizer, 0, wx.EXPAND, 1)
        rtsp_sizer.Add(username_sizer, 0, wx.EXPAND, 1)
        rtsp_sizer.Add(password_sizer, 0, wx.EXPAND, 1)
        play = wx.Button(self, wx.ID_ANY, u"预览", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        save = wx.Button(self, wx.ID_ANY, u"保存", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        play.Bind(wx.EVT_BUTTON, self.OnPlay)
        save.Bind(wx.EVT_BUTTON, self.OnSave)
        rtsp_sizer.Add(play, 0, wx.EXPAND | wx.ALL, 0)
        rtsp_sizer.Add(save, 0, wx.EXPAND | wx.ALL, 0)
        return rtsp_sizer

    def __get_config(self, name):
        return Utility.ParseConfig.get(path=Path.CONFIG, section=name)

    def before_test(self):
        super(FPVTest, self).before_test()
        self.player.Stop()

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")
        self.player.Stop()
        self.player.Hide()

    def OnPlay(self, event):
        if not self.player.IsShown():
            self.player.Show()
        self.player.Open(self.GetUrl())
        self.player.Play()

    def OnSave(self, event):
        data = dict()
        data["address"] = self.address.GetValue()
        data["port"] = self.port.GetValue()
        data["username"] = self.username.GetValue()
        data["password"] = self.password.GetValue()
        Utility.ParseConfig.modify(path=Path.CONFIG, data={"rtsp": data})

    def GetUrl(self):
        return "rtsp://{username}:{password}@{address}:{port}".format(
            username=self.username.GetValue(),
            password=self.password.GetValue(),
            port=self.port.GetValue(),
            address=self.address.GetValue(),
        )


class Player(wx.Frame):
    def __init__(self, EVT_RESULT, position=wx.DefaultPosition):
        wx.Frame.__init__(self, None, wx.ID_ANY, u"预览图", pos=position, size=(550, 350), style=wx.CAPTION)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.EVT_RESULT = EVT_RESULT
        self.preview = wx.Panel(self, wx.ID_ANY)
        self.preview.SetBackgroundColour(wx.BLACK)
        result_sizer = self.init_result_sizer()
        sizer.Add(self.preview, 1, flag=wx.EXPAND | wx.ALL, border=1)
        sizer.Add(result_sizer, 0, flag=wx.EXPAND | wx.ALL, border=1)
        self.SetSizer(sizer)
        self.Center()
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def Open(self, url):
        self.Stop()
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.set_hwnd(self.preview.GetHandle())
        if self.player.play() == -1:
            Utility.Alert.Error("无法播放")

    def Play(self):
        self.player.play()

    def Stop(self):
        self.player.stop()

    def Destroy(self):
        self.player.stop()
        return self.Hide()

    def init_result_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        Pass = self.create_result_button(True)
        Fail = self.create_result_button(False)
        sizer.Add(Pass, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(Fail, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def create_result_button(self, isPass):
        color = Color.SpringGreen3 if isPass else Color.Firebrick2
        label = u"PASS" if isPass else u"FAIL"
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0)
        button.SetBackgroundColour(color)
        button.SetFont(Font.COMMON_1_LARGE_BOLD)
        button.Bind(wx.EVT_BUTTON, self.EVT_RESULT)
        return button
