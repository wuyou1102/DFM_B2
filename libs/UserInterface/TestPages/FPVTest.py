# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color
from libs import Utility
import vlc

logger = logging.getLogger(__name__)
url = "rtsp://admin:Password01!@192.168.1.155:554"


class FPVTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"图传测试", flag="FPV")
        self.player = Player(self.on_result_button)

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.url = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.url.SetValue(url)
        self.url.SetFont(Font.COMMON_1_LARGE)
        play = wx.Button(self, wx.ID_ANY, u"预览", wx.DefaultPosition, wx.DefaultSize, 0)
        play.Bind(wx.EVT_BUTTON, self.OnPlay)

        url_sizer.Add(self.url, 1, wx.EXPAND | wx.ALL, 1)
        url_sizer.Add(play, 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(url_sizer, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

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
        self.player.Open(self.url.GetValue())
        self.player.Play()


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
