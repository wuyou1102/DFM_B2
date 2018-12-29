# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
import matplotlib

matplotlib.use('WXAgg')
from libs import Utility
from libs.Config import Color
from libs.Config import Font
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy
from matplotlib.ticker import MultipleLocator

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"射频测试", size=(800, 600))
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
        main_sizer.Add(horizontal_0, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(horizontal_1, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(horizontal_2, 1, wx.EXPAND | wx.ALL, 0)
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
        self.panel_mpl = MatplotPanel(self)
        sizer.Add(self.panel_mpl, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_write_sn_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        return sizer


class FrequencySettingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.list_2_4 = ['2410', '2450', '2475']
        self.list_5_8 = ['5750', '5800', '5825']
        main_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"频点"), wx.VERTICAL)
        radio_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.radio_rx = wx.RadioButton(self, wx.ID_ANY, u"接收", wx.DefaultPosition, wx.DefaultSize, 0, name='receive')
        self.radio_tx = wx.RadioButton(self, wx.ID_ANY, u"发送", wx.DefaultPosition, wx.DefaultSize, 0, name='transmit')
        self.radio_rx.Bind(wx.EVT_RADIOBUTTON, self.__on_radio_change)
        self.radio_tx.Bind(wx.EVT_RADIOBUTTON, self.__on_radio_change)

        radio_sizer.Add(self.radio_rx, 1, wx.ALL, 0)
        radio_sizer.Add(self.radio_tx, 1, wx.ALL, 0)
        current_sizer = wx.BoxSizer(wx.HORIZONTAL)
        height = 25
        current_title = wx.StaticText(self, wx.ID_ANY, u"当前:  ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_value = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (-1, height), 0)
        pic_refresh = wx.Image('resource/icon/Refresh.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        refresh = wx.BitmapButton(self, wx.ID_ANY, pic_refresh, wx.DefaultPosition, (height, height), style=0)
        refresh.Bind(wx.EVT_BUTTON, self.__on_query_freq)
        current_sizer.Add(current_title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        current_sizer.Add(self.current_value, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 0)
        current_sizer.Add(refresh, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 0)

        self.wx_choice_freq = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [u"2.4G", u"5.8G"], 0)
        self.wx_choice_freq.SetStringSelection(u"2.4G")
        self.wx_choice_freq.Bind(wx.EVT_CHOICE, self.__change_freq_choice)
        self.wx_list_freq = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.list_2_4, wx.LB_SINGLE)

        setting = wx.Button(self, wx.ID_ANY, u"设置", wx.DefaultPosition, wx.DefaultSize, 0)
        setting.Bind(wx.EVT_BUTTON, self.__on_set_freq)

        main_sizer.Add(radio_sizer, 0, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(current_sizer, 0, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(self.wx_choice_freq, 0, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(self.wx_list_freq, 1, wx.EXPAND | wx.ALL, 1)
        main_sizer.Add(setting, 0, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(main_sizer)
        self.Layout()
        self.radio_rx.SetValue(True)
        self.current_value.SetValue(self.get_receive_freq())

    def __change_freq_choice(self, event):
        lst = self.list_2_4 if self.wx_choice_freq.GetStringSelection() == u"2.4G" else self.list_5_8
        self.wx_list_freq.SetItems(lst)

    def __on_query_freq(self, event):
        point = self.get_freq_point()
        self.current_value.SetValue(point)

    def __on_set_freq(self, event):
        freq_point = self.wx_list_freq.GetStringSelection()
        if not freq_point:
            Utility.Alert.Warn(u"请选择需要设置的频点")
            return False
        self.set_freq_point(point=freq_point)

    def __on_radio_change(self, event):
        obj = event.GetEventObject()
        point = self.get_receive_freq() if obj.Name == 'receive' else self.get_transmit_freq()
        self.current_value.SetValue(point)

    def __get(self):
        pass

    def __set(self):
        pass

    def get_freq_point(self):
        if self.radio_rx.GetValue():
            return self.get_receive_freq()
        else:
            return self.get_transmit_freq()

    def get_receive_freq(self):
        logger.debug(u"查询 [接收] 频点")
        return "receive"

    def get_transmit_freq(self):
        logger.debug(u"查询 [发送] 频点")
        return "transmit"

    def set_freq_point(self, point):
        if self.radio_rx.GetValue():
            self.set_receive_freq(point)
        else:
            self.set_transmit_freq(point)

    def set_receive_freq(self, point):
        logger.debug(u"设置 [接收] 频点: \"%s\"" % point)

    def set_transmit_freq(self, point):
        logger.debug(u"设置 [发送] 频点: \"%s\"" % point)


class MatplotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u""), wx.VERTICAL)
        # 配置项『
        self.dpi = 100
        self.face_color = '#FEF9E7'
        self.title = ''
        self.data_limit_length = 80
        self.__time_interval = 1000
        # 配置项』

        self.blank_array = numpy.array([])
        self.record_flag = False
        self.workbook = None
        self.Figure = Figure((1.6, 0.9), self.dpi)
        self.line_name = None
        self.Axes = self.Figure.add_axes([0.07, 0.05, 0.92, 0.88])
        self.FigureCanvas = FigureCanvasWxAgg(self, -1, self.Figure)
        main_sizer.Add(self.FigureCanvas, 1, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(self.__init_button_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(main_sizer)
        self.Layout()

    def __init_button_sizer(self):
        def pass_fail_button(isPass):
            color = Color.SpringGreen3 if isPass else Color.Firebrick2
            label = u"成  功" if isPass else u"失  败"
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), wx.BU_AUTODRAW)
            button.SetBackgroundColour(color)
            button.SetFont(Font.COMMON_1_LARGE_BOLD)
            return button

        sizer = wx.BoxSizer(wx.VERTICAL)
        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row2 = wx.BoxSizer(wx.HORIZONTAL)
        size1 = (-1, 25)
        Start = wx.Button(self, wx.ID_ANY, u"开始记录", wx.DefaultPosition, size1, 0)
        Stop = wx.Button(self, wx.ID_ANY, u"停止记录", wx.DefaultPosition, size1, 0)
        Clear = wx.Button(self, wx.ID_ANY, u"清除记录", wx.DefaultPosition, size1, 0)
        Pass = pass_fail_button(True)
        Fail = pass_fail_button(False)
        row1.Add(Start, 0, wx.ALL, 1)
        row1.Add(Stop, 0, wx.ALL, 1)
        row1.Add(Clear, 0, wx.ALL, 1)
        row2.Add(Pass, 1, wx.EXPAND | wx.ALL, 1)
        row2.Add(Fail, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(row1, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(row2, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 0)
        return sizer

    def on_start(self, event):
        pass

    def on_stop(self, event):
        pass

    def on_clear(self, event):
        pass

    def on_pass(self, event):
        pass

    def on_fail(self, event):
        pass
