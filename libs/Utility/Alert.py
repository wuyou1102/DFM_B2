# -*- encoding:UTF-8 -*-
import wx
import logging

logger = logging.getLogger(__name__)


def Info(Message, From=None):
    title = u"消息" if From is None else u"来自 \"%s\" 的消息" % From
    logger.info('{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, title, wx.OK | wx.ICON_INFORMATION)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()


def Warn(Message, From=None):
    title = u"警告" if From is None else u"来自 \"%s\" 的警告" % From
    logger.warn('{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, From, wx.OK | wx.ICON_WARNING)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()


def Error(Message, From=None):
    title = u"错误" if From is None else u"来自 \"%s\" 的错误" % From
    logger.error('{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, From, wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()
