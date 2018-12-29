# -*- encoding:UTF-8 -*-

import logging
import sys
import wx
import TestPages

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"B3测试工具 Ver.0.0.0", size=(500, 500))
        self.Center()
        self.note_pages = list()
        notebook = wx.Notebook(self)
        for note_page in TestPages.NEED_DISPLAY:
            page = note_page(parent=notebook)
            self.note_pages.append(page)
            notebook.AddPage(page, page.name)
