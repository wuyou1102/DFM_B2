# -*- encoding:UTF-8 -*-
import wx
import logging
import Base

logger = logging.getLogger(__name__)


class USBTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"USB测试")

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        return sizer
