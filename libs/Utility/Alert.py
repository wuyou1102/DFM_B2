# -*- encoding:UTF-8 -*-
import logging

import wx

logger = logging.getLogger(__name__)


def Info(Message, From=None):
    title = u"消息" if From is None else u"来自 \"%s\" 的消息" % From
    logger.info(u'{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, title, wx.OK | wx.ICON_INFORMATION)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()


def Warn(Message, From=None):
    title = u"警告" if From is None else u"来自 \"%s\" 的警告" % From
    logger.warn(u'{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, title, wx.OK | wx.ICON_WARNING)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()


def Error(Message, From=None):
    title = u"错误" if From is None else u"来自 \"%s\" 的错误" % From
    logger.error(u'{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, title, wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()


class CountdownDialog(wx.Dialog):
    def __init__(self, Message):
        wx.Dialog.__init__(self, parent=None, id=wx.ID_ANY, title=u"倒计时", size=(300, 100), pos=wx.DefaultPosition,
                           style=wx.CAPTION | wx.ICON_INFORMATION | wx.OK)
        self.panel = wx.Panel(self)
        self.countdown = 0
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(self.panel, wx.ID_ANY, Message, wx.DefaultPosition, wx.DefaultSize,
                                     wx.ALIGN_CENTER_HORIZONTAL)
        self.wx_countdown = wx.StaticText(self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.message.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.wx_countdown.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        main_sizer.Add(self.message, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(self.wx_countdown, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Layout()
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)  # 绑定一个定时器事件

    def Countdown(self, countdown):
        self.countdown = countdown
        self.timer.Start(1000)
        self.ShowModal()

    def OnTimer(self, event):
        self.wx_countdown.SetLabel(str(self.countdown))
        self.countdown -= 1
        if self.countdown == 0:
            self.timer.Stop()
            self.Destroy()
