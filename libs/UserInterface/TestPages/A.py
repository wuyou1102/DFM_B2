# -*- encoding:UTF-8 -*-
import wx
import logging
import Base

logger = logging.getLogger(__name__)


class A(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name="网口测试1233", color="blue")
