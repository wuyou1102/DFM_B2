# -*- encoding:UTF-8 -*-
import logging
import matplotlib
import wx
import Base
from libs import Utility
from libs.Config import Font
from libs.Config import Picture

matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy
from libs.Config import Color

logger = logging.getLogger(__name__)


class ReceiveBase(Base.TestPage):
    def __init__(self, parent, type, freq):
        self.freq = freq
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.init_variable()

    def GetSignalSources(self):
        return self.Parent.Parent.Parent.Parent.SignalSources

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 0, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_rssi_sizer(), 1, wx.EXPAND | wx.LEFT, 50)
        hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.RIGHT, 5)
        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.LEFT, 15)
        sizer.Add(self.__init_message_sizer(), 0, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, 15)
        sizer.Add(self.__init_mpl_sizer(), 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_message_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status = wx.StaticBitmap(self, wx.ID_ANY, Picture.status_disconnect, wx.DefaultPosition, (33, 33), 0)
        self.message = wx.StaticText(self, wx.ID_ANY, u"正在连接信号发生器", wx.DefaultPosition, wx.DefaultSize, 0)
        self.message.SetFont(Font.DESC)
        sizer.Add(self.status, 0, wx.ALL, 1)
        sizer.Add(self.message, 1, wx.EXPAND | wx.TOP, 3)
        return sizer

    def __init_mpl_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_mpl = BlerMpl(self)
        sizer.Add(self.panel_mpl, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_rssi_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        rssi_0_title = wx.StaticText(self, wx.ID_ANY, u"天线0: ", wx.DefaultPosition, wx.DefaultSize, 0)
        rssi_1_title = wx.StaticText(self, wx.ID_ANY, u"天线1: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.rssi_0 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (50, -1),
                                  wx.TE_READONLY | wx.TE_CENTRE)
        self.rssi_0.SetBackgroundColour(Color.LightGray)
        self.rssi_1 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (50, -1),
                                  wx.TE_READONLY | wx.TE_CENTRE)
        self.rssi_1.SetBackgroundColour(Color.LightGray)
        sizer.Add(rssi_0_title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.rssi_0, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(rssi_1_title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.rssi_1, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (60, -1), wx.TE_READONLY)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        button = wx.Button(self, wx.ID_ANY, u"重设频点", wx.DefaultPosition, (65, 27), 0, name=str(self.freq))
        button.Bind(wx.EVT_BUTTON, self.reset_frequency)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def reset_frequency(self, event):
        obj = event.GetEventObject()
        uart = self.get_communicat()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_communicat()
        uart.set_qam(value=selected)
        self.update_current_mcs()

    def __init_status_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        restart = wx.BitmapButton(self, wx.ID_ANY, Picture.restart, wx.DefaultPosition, (33, 33), 0)
        restart.Bind(wx.EVT_BUTTON, self.on_restart)
        sizer.Add(restart, 0, wx.ALL, 1)
        return sizer

    def __init_mcs_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"调制方式: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_mcs = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     ["BPSK", "QPSK", "16QAM", "64QAM"], 0)
        self.current_mcs.Bind(wx.EVT_CHOICE, self.on_mcs_selected)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_mcs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def update_current_freq_point(self):
        def update_freq():
            self.Sleep(0.05)
            uart = self.get_communicat()
            value = uart.get_frequency_point()
            self.current_point.SetValue(value)
            if float(value) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")

        Utility.append_thread(target=update_freq, allow_dupl=True)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_communicat()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs, allow_dupl=True)

    def before_test(self):
        signal_sources = self.GetSignalSources()
        self.PassButton.Disable()
        if signal_sources is not None:
            signal_sources.SetFrequency(self.freq)
        self.init_variable()
        self.panel_mpl.init_axes()
        uart = self.get_communicat()
        uart.set_rx_mode_20m()
        uart.set_frequency_point(self.freq * 1000)
        self.update_current_freq_point()

    def init_variable(self):
        self.stop_flag = True
        self.lst_slot = []
        self.lst_rssi0 = []
        self.lst_rssi1 = []

    def start_test(self):
        self.FormatPrint(info="Started")
        Utility.append_thread(target=self.draw_line, thread_name="DRAW_LINE_%s" % self.freq)

    def stop_test(self):
        self.stop_flag = False
        self.FormatPrint(info="Stop")

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def draw_line(self):
        comm = self.get_communicat()
        self.Sleep(1)
        while self.stop_flag:
            if comm.is_instrument_connected():
                self.status.SetBitmap(Picture.status_connect1)
                self.message.SetLabel(u"信号发生器已连接，测试中")
                break
            else:
                self.message.SetLabel(u"正在连接信号发生器")
                self.status.SetBitmap(Picture.status_disconnect)
                comm.hold_baseband()
                self.status.SetBitmap(wx.NullBitmap)
                comm.release_baseband()
        for x in range(40):
            if not self.stop_flag:
                return
            self.update_bler()
            self.panel_mpl.refresh(self.lst_slot)
            self.Sleep(1)
            if self.check_result():
                self.set_message_result(isPass=True)
                self.SetResult("PASS")
                return
        self.set_message_result(isPass=False)
        self.SetResult("FAIL")

    def check_result(self):
        logger.debug(u"天线0平均信号强度：%s" % (sum(self.lst_rssi0) / len(self.lst_rssi0)))
        logger.debug(u"天线1平均信号强度：%s" % (sum(self.lst_rssi1) / len(self.lst_rssi1)))
        if self.lst_slot.count(0) >= 10:
            return True
        return False

    def set_message_result(self, isPass=True):
        if isPass:
            self.message.SetLabel(u"测试通过，请点击PASS")
        else:
            self.message.SetLabel(u"测试失败，请点击FAIL")

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_communicat()
            uart.hold_baseband()
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
            if uart.is_instrument_connected():
                self.status.SetBitmap(Picture.status_connect1)
            else:
                self.status.SetBitmap(Picture.status_disconnect)
        finally:
            obj.Enable()

    def update_bler(self):
        uart = self.get_communicat()
        result = uart.get_rssi_and_bler()
        if result is not None and int(result, 16) > 0:
            bler = int(result[8:], 16)
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            self.lst_slot.append(bler)
            self.lst_rssi0.append(rssi0)
            self.lst_rssi1.append(rssi1)
            self.rssi_0.SetValue(str(rssi0))
            self.rssi_1.SetValue(str(rssi1))
        else:
            self.update_bler()

    def get_bler(self, func):
        value = func()
        try:
            block = int(value, 16)
            return block
        except ValueError:
            return self.get_bler(func=func)


class BaseMplPanel(wx.Panel):
    def __init__(self, parent, name, unit):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        self.title = name + unit
        self.name = name
        self.unit = unit
        self.data = None
        MplSizer = wx.BoxSizer(wx.VERTICAL)
        # 配置项『
        self.dpi = 100
        self.facecolor = '#FEF9E7'
        self.data_limit_length = 30
        self.y_max = 128
        # 配置项』
        self.x_limit_range = numpy.arange(self.data_limit_length)
        self.blank_array = numpy.array([])
        self.Figure = Figure((1.6, 0.9), self.dpi)
        self.Figure.set_facecolor("#E0EEEE")
        self.Axes = self.Figure.add_axes([0.05, 0.02, 0.93, 0.96])
        self.FigureCanvas = FigureCanvasWxAgg(self, -1, self.Figure)
        MplSizer.Add(self.FigureCanvas, 1, wx.EXPAND | wx.ALL, 0)
        MainSizer.Add(MplSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)
        self.SetSizer(MainSizer)
        self.Update()

    def __init_setting_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        y_set_sizer = self.__init_ybound_set_sizer()
        button_sizer = self.__init_button_sizer()
        sizer.Add(y_set_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        return sizer

    def __init_button_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(self, wx.ID_ANY, u"保存当前截图", wx.DefaultPosition, (80, -1), 0)
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        sizer.Add(save_button, 0, wx.EXPAND | wx.ALL, 2)
        return sizer

    def init_ybound_set_sizer(self, parent):
        y_set_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(parent, wx.ID_ANY, u"%s范围: " % self.name, wx.DefaultPosition, wx.DefaultSize,
                              style=wx.TEXT_ALIGNMENT_CENTER)
        to = wx.StaticText(parent, wx.ID_ANY, u"～", wx.DefaultPosition, wx.DefaultSize,
                           style=wx.TEXT_ALIGNMENT_CENTER)
        unit_title = wx.StaticText(parent, wx.ID_ANY, self.unit, wx.DefaultPosition, wx.DefaultSize,
                                   style=wx.TEXT_ALIGNMENT_CENTER)
        self.min_tc = wx.TextCtrl(parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (50, -1),
                                  wx.TE_RIGHT | wx.TE_PROCESS_ENTER)
        self.max_tc = wx.TextCtrl(parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (50, -1),
                                  wx.TE_RIGHT | wx.TE_PROCESS_ENTER)

        self.max_tc.Bind(wx.EVT_TEXT_ENTER, self.update_ybound)
        self.min_tc.Bind(wx.EVT_TEXT_ENTER, self.update_ybound)
        y_set_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        y_set_sizer.Add(self.min_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        y_set_sizer.Add(to, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        y_set_sizer.Add(self.max_tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        y_set_sizer.Add(unit_title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        return y_set_sizer

    def update_ybound(self, event):
        try:
            y_max = int(self.max_tc.GetValue())
            y_min = int(self.min_tc.GetValue())
            if y_max < y_min:
                y_min, y_max = y_max, y_min
            self.set_ybound(lower=y_min, upper=y_max)
            Utility.AlertMsg(u"设置成功")
        except ValueError:
            Utility.AlertError(u"输入异常: \"%s\" or \"%s\"" % (self.min_tc.GetValue(), self.max_tc.GetValue()))

    def get_title(self):
        return self.title

    def close_timer(self):
        self.timer.Stop()

    def refresh(self, event):
        raise NotImplementedError('MPL must have refresh function')

    def get_object(self):
        return self.obj

    def update(self):
        self.FigureCanvas.draw()

    def set_ybound(self, lower, upper):
        self.Axes.set_ybound(lower=lower, upper=upper)

    def init_axes(self, x_lower=0, x_upper=None):
        if x_upper is None:
            x_upper = self.data_limit_length
        self.Axes.set_facecolor(self.facecolor)
        self.Axes.set_xbound(lower=x_lower, upper=x_upper)
        self.Axes.set_ybound(-1, self.y_max)
        self.Axes.yaxis.grid(True)
        self.Axes.xaxis.grid(True)
        self.Axes.xaxis.set_visible(False)
        self.Axes.tick_params(labelsize=9, direction='in', grid_alpha=0.3)  # 设置坐标系文字大小
        self.update()

    def refresh_line(self, line, data):
        if len(data) < self.data_limit_length:
            line.set_xdata(numpy.arange(len(data)))
            line.set_ydata(numpy.array(data))
        else:
            line.set_xdata(self.x_limit_range)
            line.set_ydata(numpy.array(data[-self.data_limit_length:]))


class BlerMpl(BaseMplPanel):
    def __init__(self, parent):
        BaseMplPanel.__init__(self, parent, name=u"误块数", unit=u"(个)")
        self.__init_plot()
        self.init_axes()

    # def refresh(self, slot, br):
    #     self.refresh_line(self.slot, slot)
    #     self.refresh_line(self.br, br)
    #     self.update()

    def refresh(self, slot):
        self.refresh_line(self.slot, slot)
        self.update()

    def __init_plot(self):
        self.slot, = self.Axes.plot(numpy.array([]), numpy.array([]), color="blue", linewidth=1.5, label=u'SLOT',
                                    linestyle='-')
        # self.br, = self.Axes.plot(numpy.array([]), numpy.array([]), color="red", linewidth=1.5, label=u'BR',
        #                           linestyle='-')
        self.Axes.legend()
