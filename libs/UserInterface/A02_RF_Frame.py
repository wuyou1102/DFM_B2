# -*- encoding:UTF-8 -*-

import logging
import sys
import wx
from libs import Utility

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"射频测试", size=(500, 600))
        self.Center()
        self.panel = Panel(self)


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_2_4 = ['2410', '2450', '2475']
        self.list_5_8 = ['5750', '5800', '5825']
        horizontal_0 = self.__init_horizontal_0_sizer()
        horizontal_1 = self.__init_horizontal_1_sizer()
        horizontal_2 = self.__init_horizontal_2_sizer()
        main_sizer.Add(horizontal_0, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(horizontal_1, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(horizontal_2, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)
        self.Layout()

    def __init_horizontal_0_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        return sizer

    def __init_horizontal_1_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_freq = FrequencySettingPanel(self)
        sizer.Add(self.panel_freq, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_horizontal_2_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        return sizer

    def __init_write_sn_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        return sizer


class FrequencySettingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.list_2_4 = ['2410', '2450', '2475']
        self.list_5_8 = ['5750', '5800', '5825']
        self.SetBackgroundColour('red')
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        radio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radio_rx = wx.RadioButton(self, wx.ID_ANY, u"接收", wx.DefaultPosition, wx.DefaultSize, 0, name='receive')
        self.radio_tx = wx.RadioButton(self, wx.ID_ANY, u"发送", wx.DefaultPosition, wx.DefaultSize, 0, name='transmit')
        self.radio_rx.SetValue(True)
        radio_sizer.Add(self.radio_rx, 1, wx.ALL, 0)
        radio_sizer.Add(self.radio_tx, 1, wx.ALL, 0)

        self.wx_choice_freq = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [u"2.4G", u"5.8G"], 0)
        self.wx_choice_freq.SetStringSelection(u"2.4G")
        self.wx_choice_freq.Bind(wx.EVT_CHOICE, self.__change_freq_choice)
        self.wx_list_freq = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.list_2_4, wx.LB_SINGLE)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_get = wx.Button(self, wx.ID_ANY, u"查询当前", wx.DefaultPosition, wx.DefaultSize, 0)
        button_set = wx.Button(self, wx.ID_ANY, u"设置频点", wx.DefaultPosition, wx.DefaultSize, 0)
        button_get.Bind(wx.EVT_BUTTON, self.__on_query_freq)
        button_set.Bind(wx.EVT_BUTTON, self.__on_set_freq)
        button_sizer.Add(button_get, 1, wx.ALL, 0)
        button_sizer.Add(button_set, 1, wx.ALL, 0)
        main_sizer.Add(radio_sizer, 0, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(self.wx_choice_freq, 0, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(self.wx_list_freq, 1, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(main_sizer)
        self.Layout()

    def __change_freq_choice(self, event):
        lst = self.list_2_4 if self.wx_choice_freq.GetStringSelection() == u"2.4G" else self.list_5_8
        self.wx_list_freq.SetItems(lst)

    def __on_query_freq(self, event):
        temp = "5666"
        if int(temp) < 5000:
            self.wx_choice_freq.SetStringSelection(u"2.4G")
            self.wx_list_freq.SetItems(self.list_2_4)
        else:
            self.wx_choice_freq.SetStringSelection(u"5.8G")
            self.wx_list_freq.SetItems(self.list_5_8)
        if temp not in self.wx_list_freq.Items:
            self.wx_list_freq.Append(temp)
        self.wx_list_freq.SetStringSelection(temp)

    def __on_set_freq(self, event):
        freq_point = self.wx_list_freq.GetStringSelection()
        if not freq_point:
            Utility.Alert.Warn(u"请选择需要设置的频点")
            return
        if self.radio_rx.GetValue():
            logger.debug(u"设置 [接收] 频点: \"%s\"" % freq_point)
            self.set_receive_freq(freq_point)
        else:
            logger.debug(u"设置 [发送] 频点: \"%s\"" % freq_point)
            self.set_transmit_freq(freq_point)

    def __get(self):
        pass

    def __set(self):
        pass

    def get_receive_freq(self):
        pass

    def get_transmit_freq(self):
        pass

    def set_receive_freq(self, point):
        pass

    def set_transmit_freq(self, point):
        pass
