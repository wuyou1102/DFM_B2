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

logger = logging.getLogger(__name__)


class FPV(Base.TestPage):
    def __init__(self, parent, type):
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.player = None

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
        super(FPV, self).before_test()

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")
        if self.player is not None:
            self.player.Destroy()
            self.player = None

    def OnPlay(self, event):
        if self.player is None:
            self.player = Player(self.on_result_button)
            self.player.Show(url=self.GetUrl())
        else:
            self.player.Reload(url=self.GetUrl())

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

    @staticmethod
    def GetName():
        return u"图传测试"

    @staticmethod
    def GetFlag(t):
        if t in ["MACHINE", u"整机"]:
            return String.FPV_MACHINE


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
        self.url = ""

    def Show(self, url, show=True):
        self.url = url
        self.Init(url=url)
        super(Player, self).Show(show=show)
        self.Play()

    def Reload(self, url):
        if self.url != url:
            self.Stop()
            self.Init(url=url)
            self.Play()

    def Destroy(self):
        Utility.append_thread(target=self.Stop, allow_dupl=False, thread_name=str(self))
        super(Player, self).Destroy()

    def Init(self, url):
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.set_hwnd(self.preview.GetHandle())

    def Play(self):
        self.player.play()

    def Stop(self):
        self.player.stop()

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
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0, name=label)
        button.SetBackgroundColour(color)
        button.SetFont(Font.COMMON_1_LARGE_BOLD)
        button.Bind(wx.EVT_BUTTON, self.EVT_RESULT)
        return button
