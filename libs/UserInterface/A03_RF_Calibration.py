# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
import A01_CIT_Base
from libs.Config import Color
from ObjectListView import FastObjectListView, ColumnDefn, Filter

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')

CLOSE_LOOP_INITIAL_VALUE = {
    '24': (0x09, 0x68),
    '23': (0x0B, 0x65),
    '22': (0x0D, 0x61),
    '21': (0x0E, 0x5E),
    '20': (0x0F, 0x5A),
    '19': (0x10, 0x57),
    '18': (0x11, 0x54),
    '17': (0x12, 0x50),
    '16': (0x14, 0x4D),
    '15': (0x15, 0x4A),
    '14': (0x16, 0x47),
    '13': (0x17, 0x44),
    '12': (0x18, 0x41),
    '11': (0x19, 0x3E),
    '10': (0x1A, 0x3B),
    '9': (0x1B, 0x37),
    '8': (0x1C, 0x34),
    '7': (0x1D, 0x31),
    '6': (0x1E, 0x2E),
    '5': (0x1F, 0x2B),
}


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"射频校准", size=(800, 600))
        self.panel = Panel(self)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(A01_CIT_Base.Panel):
    def __init__(self, parent):
        A01_CIT_Base.Panel.__init__(self, parent=parent, type_="")

    def __init_test_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.test_view = CalibrationPanel(parent=self)
        sizer.Add(self.test_view, 1, wx.EXPAND | wx.ALL, 0)
        return sizer


class CalibrationPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.result_controls = list()
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_view = FastObjectListView(
            self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER | wx.LC_NO_SORT_HEADER)
        self.main_sizer.Add(self.list_view, 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.__set_columns()
        self.__set_row_formatter()
        self.clear_case_result()

    def clear_case_result(self):
        print 's'
        for _ in range(24, 4, -1):
            data = CLOSE_LOOP_INITIAL_VALUE.get(str(_))
            obj = CalibrationData(level=_, gain=data[0], init_value=data[1])
            self.list_view.AddObject(obj)

    def update_case_result(self):
        pass

    def __set_columns(self):
        self.list_view.SetColumns(
            [
                ColumnDefn(title=u"", align="right", width=0, valueGetter=''),
                ColumnDefn(title=u"level", align="center", width=100, valueGetter='_level'),
                ColumnDefn(title=u"ref gain", align="center", width=100, valueGetter='_gain'),
                ColumnDefn(title=u"初始功率值", align="center", width=100, valueGetter='_init_value'),
                ColumnDefn(title=u"校准功率值", align="center", width=100, valueGetter='_cali_value'),
                ColumnDefn(title=u"信号强度", align="center", width=100, valueGetter='_rssi'),
            ]
        )

    def __set_row_formatter(self):
        self.list_view.rowFormatter = self.row_formatter

    @staticmethod
    def row_formatter(list_view, item):
        pass

    def __init_value(self):
        pass


class CalibrationData(object):
    def __init__(self, level, gain, init_value):
        self._level = level
        self._gain = hex(gain).upper()
        self._init_value = hex(init_value).upper()
        self._cali_value = ""
        self._rssi = ""


    def