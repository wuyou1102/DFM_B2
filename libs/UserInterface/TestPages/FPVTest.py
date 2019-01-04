# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs import Utility
import vlc

logger = logging.getLogger(__name__)
url = "rtsp://admin:admin@192.168.1.103:554"


class FPVTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"图传测试", flag="FPV")
        self.player = None

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.url = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.url.SetValue(url)
        self.url.SetFont(Font.COMMON_1_LARGE)
        play = wx.Button(self, wx.ID_ANY, u"Play", wx.DefaultPosition, wx.DefaultSize, 0)
        play.Bind(wx.EVT_BUTTON, self.on_play)
        url_sizer.Add(self.url, 1, wx.EXPAND | wx.ALL, 1)
        url_sizer.Add(play, 0, wx.EXPAND | wx.ALL, 1)
        self.view = wx.Panel(self, wx.ID_ANY)
        self.view.SetBackgroundColour(wx.BLACK)
        sizer.Add(url_sizer, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.view, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def before_test(self):
        super(FPVTest, self).before_test()
        self.on_stop(None)

    def start_test(self):
        self.FormatPrint(info="Started")

    def stop_test(self):
        self.FormatPrint(info="Stop")
        self.on_stop(None)

    def on_play(self, event):
        Utility.append_thread(target=self.__play, allow_dupl=False)

    def __play(self):
        instance = vlc.Instance()
        self.player = instance.media_player_new()
        self.player.set_hwnd(self.view.GetHandle())
        rtsp = instance.media_new(self.url.GetValue())
        self.player.set_media(rtsp)
        if self.player.play() == -1:
            Utility.Alert.Error(u"播放失败")
        else:
            self.EnablePass()

    def on_stop(self, event):
        if self.player is not None:
            self.player.stop()
