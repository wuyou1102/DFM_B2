# -*- encoding:UTF-8 -*-
import wx
import logging
import Base

logger = logging.getLogger(__name__)


class B(Base.Page):
    def __init__(self, parent):
        Base.Page.__init__(self, parent=parent, name="B", color="red")
