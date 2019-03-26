# -*- encoding:UTF-8 -*-
__author__ = 'wuyou'

import sys
import wx

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    app = wx.App()
    from libs.UserInterface.A00_Entrance import Frame

    f = Frame()
    f.Show()
    app.MainLoop()

