# -*- encoding:UTF-8 -*-
import logging
import sys
import wx
import A01_CIT_Base
from libs.Config import Color
from ObjectListView import FastObjectListView, ColumnDefn, Filter
import time

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')

CLOSE_LOOP_INITIAL_VALUE = {
    '5800': {
        '27': (0x03, 0x74),
        '26': (0x05, 0x70),
        '25': (0x07, 0x6c),
        '24': (0x09, 0x69),
        '23': (0x0B, 0x66),
        '22': (0x0D, 0x62),
        '21': (0x0E, 0x5F),
        '20': (0x0F, 0x5C),
        '19': (0x10, 0x58),
        '18': (0x11, 0x55),
        '17': (0x12, 0x52),
        '16': (0x14, 0x4F),
        '15': (0x15, 0x4B),
        '14': (0x16, 0x48),
        '13': (0x17, 0x44),
        '12': (0x18, 0x41),
        '11': (0x19, 0x3E),
        '10': (0x1A, 0x3B),
        '9': (0x1B, 0x38),
        '8': (0x1C, 0x34),
        '7': (0x1D, 0x31),
        '6': (0x1E, 0x2E),
        '5': (0x1F, 0x2B),
    },
    '2400': {
        '20': (0x0A, 0x52),
        '19': (0x0B, 0x4E),
        '18': (0x0C, 0x4B),
        '17': (0x0D, 0x48),
        '16': (0x0E, 0x45),
        '15': (0x0F, 0x42),
        '14': (0x10, 0x3F),
        '13': (0x11, 0x3C),
        '12': (0x12, 0x39),
        '11': (0x13, 0x36),
        '10': (0x14, 0x33),
        '9': (0x15, 0x30),
        '8': (0x16, 0x2D),
        '7': (0x17, 0x2A),
        '6': (0x18, 0x28),
        '5': (0x19, 0x26),
        '4': (0x1A, 0x24),
        '3': (0x1B, 0x22),
        '2': (0x1C, 0x20),
        '1': (0x1D, 0x1F),
    }
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

    def disconnect(self, error_msg=None):
        super(Panel, self).disconnect(error_msg=error_msg)
        self.test_view.clear_case_result()


class CalibrationPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.result_controls = list()
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_view = FastObjectListView(
            self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER | wx.LC_NO_SORT_HEADER)
        self.main_sizer.Add(self.list_view, 8, wx.EXPAND | wx.ALL, 1)
        self.main_sizer.Add(self.__init_operation_sizer(), 2, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.__set_columns()
        self.__set_row_formatter()

    def __init_operation_sizer(self):
        def create_button(label, name):
            btn = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (100, 35), 0, name=name)
            btn.Bind(wx.EVT_BUTTON, self.on_button_click)
            return btn

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(create_button(u"校准参数", "calibrate"), 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizer.Add(create_button(u"导入到设备", "import"), 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizer.Add(create_button(u"保存到文件", "export"), 0, wx.ALIGN_CENTER | wx.ALL, 0)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "calibrate":
            self._calibrate()
        elif name == "import":
            pass
        elif name == "export":
            pass

    def _calibrate(self):
        device = self.parent.get_variable("socket")
        device.set_tx_mode_20m()
        for obj in self.list_view.GetObjects():
            try:
                obj.calibrate(device=device)
                self.list_view.RefreshObject(obj)
            except StopIteration:
                break

    def _export(self):
        pass

    def _import(self):
        pass

    def clear_case_result(self):
        self.list_view.RemoveObjects(self.list_view.GetObjects())

    def update_case_result(self):
        init_value_2400 = CLOSE_LOOP_INITIAL_VALUE['2400']
        init_value_5800 = CLOSE_LOOP_INITIAL_VALUE['5800']

        for level in range(27, 4, -1):
            data = init_value_5800.get(str(level))
            obj = CalibrationData(freq="5800", level=level, gain=data[0], init_power=data[1], parent=self)
            self.list_view.AddObject(obj)
        for level in range(20, 0, -1):
            data = init_value_2400.get(str(level))
            obj = CalibrationData(freq="2400", level=level, gain=data[0], init_power=data[1], parent=self)
            self.list_view.AddObject(obj)

    def __set_columns(self):
        self.list_view.SetColumns(
            [
                ColumnDefn(title=u"", align="right", width=0, valueGetter=''),
                ColumnDefn(title=u"频段", align="center", width=100, valueGetter='_freq_band'),
                ColumnDefn(title=u"level", align="center", width=100, valueGetter='_level'),
                ColumnDefn(title=u"ref gain", align="center", width=100, valueGetter='_gain'),
                ColumnDefn(title=u"初始功率值", align="center", width=100, valueGetter='_init_power'),
                ColumnDefn(title=u"信号强度", align="center", width=100, valueGetter='_rssi'),
                ColumnDefn(title=u"校准功率值", align="center", width=100, valueGetter='_cali_power'),
            ]
        )

    def __set_row_formatter(self):
        self.list_view.rowFormatter = self.row_formatter

    @staticmethod
    def row_formatter(list_view, item):
        pass

    def __init_value(self):
        pass


UNIT = 0.33


class CalibrationData(object):
    def __init__(self, freq, level, gain, init_power, parent):
        self.parent = parent
        self._freq_band = freq
        self._level = level
        self._upper_level = level + 0.2
        self._lower_level = level - 0.2
        self._upper_limit_level = level + 1
        self._lower_limit_level = level - 1
        self._gain = hex(gain).upper()
        self.__gain = gain
        self._init_power = hex(init_power).upper()
        self.__init_power = init_power
        self._cali_power = ""
        self._rssi = ""

    def calibrate(self, device, instrument=None):
        if instrument is None:
            self.switch_power(device=device)
            time.sleep(2)
            rssi = self.rssi_input()
        else:
            rssi = ""
        if rssi is None:
            raise StopIteration
        else:
            self._rssi, self._cali_power = self.analyze_input_rssi(rssi_value=rssi)

    def analyze_input_rssi(self, rssi_value):
        try:
            rssi_value = float(rssi_value)
        except ValueError:
            return u"错误的输入", "ERROR"
        if self._lower_limit_level < rssi_value < self._upper_limit_level:  # 最大上下限
            if self._lower_level <= rssi_value <= self._upper_level:
                return rssi_value, self._init_power
            else:
                if rssi_value <= self._lower_level:
                    cali_power = self.__init_power + self.calc_gap(rssi_value, self._level)
                else:
                    cali_power = self.__init_power - self.calc_gap(rssi_value, self._level)
                return rssi_value, hex(cali_power).upper()
        else:
            return rssi_value, "ERROR"

    def calc_gap(self, a, b):
        diff = abs(a - b)
        return int(round(diff / UNIT))

    def switch_power(self, device):
        device.set_frequency_point(self._freq_band + '000')
        if self._freq_band == '2400':
            device.disable_tssi_2g()
            device.set_gain_and_power(self.__gain, self.__init_power)
            device.enable_tssi_2g()
        else:
            device.disable_tssi_5g()
            device.set_gain_and_power(self.__gain, self.__init_power)
            device.enable_tssi_5g()

    def get_current_pwr(self, device):
        string = device.get_gain_and_power()
        if string == "0000000000000000":
            return self.get_current_pwr(device)
        else:
            return int(string[-4:-2], 16)

    def rssi_input(self):
        try:
            dlg = wx.TextEntryDialog(self.parent, u'请输入仪器上的信号强度值(dBm)', u"")
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            return None
        finally:
            dlg.Destroy()
