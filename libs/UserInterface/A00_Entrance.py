# -*- encoding:UTF-8 -*-

import logging
import sys
import wx

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"DFM V0.1", size=(250, 200),
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.panel = Panel(self)

    def Close(self):
        self.Destroy()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        CIT = wx.Button(self, wx.ID_ANY, u"工程测试", wx.DefaultPosition, wx.DefaultSize, 0)
        RF = wx.Button(self, wx.ID_ANY, u"射频测试", wx.DefaultPosition, wx.DefaultSize, 0)
        CIT.Bind(wx.EVT_BUTTON, self.open_cit_test)
        RF.Bind(wx.EVT_BUTTON, self.open_rf_test)
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(CIT, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        button_sizer.Add(RF, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(button_sizer, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 15)

        self.SetSizer(main_sizer)
        self.Layout()

    def open_cit_test(self, event):
        pass

    def open_rf_test(self, event):
        print 'sss'
        from A02_RF_Frame import Frame
        f = Frame()
        f.Show()
        self.parent.Close()
