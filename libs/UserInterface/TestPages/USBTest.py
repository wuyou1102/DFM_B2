# -*- encoding:UTF-8 -*-
import wx
import logging
import Base
from libs.Config import Font
from libs.Config import Color

logger = logging.getLogger(__name__)


class USBTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name=u"USB测试", flag="USB")

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        return sizer
