# -*- encoding:UTF-8 -*-

import logging
import sys

import wx

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"DFM V0.1", size=(460, 350),
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
        tool_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"工具"), wx.HORIZONTAL)
        test_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"测试"), wx.HORIZONTAL)
        rf_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u""), wx.HORIZONTAL)
        check_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"检查"), wx.HORIZONTAL)
        WriteSN = self.__create_button(label=u"写号", name=u"WriteSN")
        # Calibration = self.__create_button(label=u"校准", name=u"Calibration")
        # Debug = self.__create_button(label=u"调试工具", name=u"Debug")
        PCBA = self.__create_button(label=u"PCBA", name=u"PCBA")
        Machine = self.__create_button(label=u"组装", name=u"Machine")
        RF = self.__create_button(label=u"射频", name=u"RF")
        RF_2_4 = self.__create_button(label=u"射频 2.4G", name=u"RF_2_4")
        RF_5_8 = self.__create_button(label=u"射频 5.8G", name=u"RF_5_8")
        FI_BS = self.__create_button(label=u"出厂检查(全向天线)", name=u"FI_O")
        FI_ND = self.__create_button(label=u"出厂检查(定向天线)", name=u"FI_D")

        tool_sizer.Add(WriteSN, 0, wx.EXPAND | wx.ALL, 5)
        # tool_sizer.Add(Calibration, 0, wx.EXPAND | wx.ALL, 5)
        # tool_sizer.Add(Debug, 0, wx.EXPAND | wx.ALL, 5)

        test_sizer.Add(PCBA, 0, wx.EXPAND | wx.ALL, 5)
        test_sizer.Add(Machine, 0, wx.EXPAND | wx.ALL, 5)
        rf_sizer.Add(RF, 0, wx.EXPAND | wx.ALL, 5)
        rf_sizer.Add(RF_2_4, 0, wx.EXPAND | wx.ALL, 5)
        rf_sizer.Add(RF_5_8, 0, wx.EXPAND | wx.ALL, 5)
        check_sizer.Add(FI_BS, 0, wx.EXPAND | wx.ALL, 5)
        check_sizer.Add(FI_ND, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(tool_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(test_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(rf_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(check_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(main_sizer)
        self.Layout()

    def __create_button(self, label, name):
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
        button.Bind(wx.EVT_BUTTON, self.__open_test)
        return button

    def __open_test(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name.startswith("RF"):
            from A01_CIT_RF import Frame
            if name == "RF_2_4":
                frame = Frame(bandwidth="2.4G")
            elif name == "RF_5_8":
                frame = Frame(bandwidth="5.8G")
            else:
                frame = Frame(bandwidth="mix")
            frame.Show()
        else:
            if name == "PCBA":
                from A01_CIT_PCBA import Frame
            elif name == "Machine":
                from A01_CIT_Machine import Frame
            elif name == "WriteSN":
                from A02_Write_Serial import Frame
            elif name == "FI_O":
                from A03_FactoryInspection_Omni import Frame
            elif name == "FI_D":
                from A03_FactoryInspection_Dire import Frame
            elif name == "Calibration":
                from A03_RF_Calibration import Frame
            elif name == "Debug":
                from A04_Debug import Frame
            frame = Frame()
            frame.Show()

        self.parent.Close()
