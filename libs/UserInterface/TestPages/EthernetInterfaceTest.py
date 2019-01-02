# -*- encoding:UTF-8 -*-
import wx
import logging
import Base

logger = logging.getLogger(__name__)


class EthernetInterfaceTest(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name="网口测试", flag="Ethernet")

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        return sizer
