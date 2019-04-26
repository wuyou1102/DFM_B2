# -*- encoding:UTF-8 -*-
import logging

import matplotlib
import wx

import Base
from libs import Utility
from libs.Config import Font
from libs.Config import Path
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
        self.stop_flag = False
        option = "2400power" if self.freq < 3000 else "5800power"
        self.power = Utility.ParseConfig.get(Path.CONFIG, "SignalSources", option=option)
        Base.TestPage.__init__(self, parent=parent, type=type)
        self.panel_mpl.init_axes()

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
        uart = self.get_communicate()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_communicate()
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
            uart = self.get_communicate()
            value = uart.get_frequency_point()
            self.current_point.SetValue(value)
            if float(value) != self.freq:
                Utility.Alert.Error(u"当前频点不是预期的频点，请手动重新设置频点。")

        Utility.append_thread(target=update_freq, thread_name="update_freq_%s" % self.freq)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_communicate()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs, allow_dupl=True)

    def before_test(self):
        self.Sleep(0.11)
        self.PassButton.Disable()
        self.panel_mpl.refresh(slot=[])
        self.message.SetLabel(u"信号发生器未连接")
        self.status.SetBitmap(Picture.status_disconnect)
        signal_sources = self.GetSignalSources()
        if signal_sources is not None:
            signal_sources.SetFrequency(self.freq)
            signal_sources.SetPower(self.power)
        uart = self.get_communicate()
        uart.set_rx_mode_20m()
        uart.set_frequency_point(self.freq * 1000)
        self.update_current_freq_point()
        self.stop_flag = False

    def start_test(self):
        self.FormatPrint(info="Started")
        if self.GetSignalSources() is None:
            Utility.append_thread(target=self.draw_line, thread_name="DRAW_LINE_%s" % self.freq)
        else:
            Utility.append_thread(target=self.auto_test_thread, thread_name="AUTO_RECEIVE_%s" % self.freq)

    def stop_test(self):
        self.stop_flag = True
        self.FormatPrint(info="Stop")

    def get_flag(self):
        return self.GetFlag(t=self.type)

    def loop(self, func, interval, **kwargs):
        logger.debug("Start Loop Function \"%s\"" % func.__name__, )
        while True:
            for x in range(interval / 50):
                if self.stop_flag:
                    logger.debug("Function \"%s\" is stopped by stop flag" % func.__name__, )
                    return
                self.Sleep(0.05)
            try:
                func(**kwargs)
            except StopIteration:
                logger.debug("Function \"%s\" is stopped by it self" % func.__name__, )
                return

    def check_instrument_connected(self, comm):
        if not comm.is_instrument_connected():
            self.message.SetLabel(u"信号发生器已连接")
            self.status.SetBitmap(Picture.status_connect1)
            raise StopIteration
        else:
            self.message.SetLabel(u"信号发生器未连接")
            self.status.SetBitmap(Picture.status_disconnect)

    def refresh_mpl(self, lst):
        self.update_bler(lst=lst)
        self.panel_mpl.refresh(slot=lst)

    def draw_line(self):
        comm = self.get_communicate()
        self.loop(self.check_instrument_connected, 1000, comm=comm)
        self.loop(self.refresh_mpl, 1000, lst=list())

    def auto_test_thread(self):
        connection_result = self.test_connection()
        if connection_result is True:
            block_result = self.test_block_error_count()
            signal_result = self.test_signal_intensity()
            if block_result is None or signal_result is None:
                self.LogMessage(u"自动测试被打断。")
                return True
            if block_result is True and signal_result is True:
                self.SetResult("PASS")
                return True
            else:
                self.SetResult("FAIL")
                return True
        elif connection_result is None:
            self.LogMessage(u"自动测试被打断。")
            return True
        else:
            self.SetResult("FAIL")
            return True

    def test_connection(self):
        comm = self.get_communicate()
        for i in range(1, 11):
            if self.stop_flag:
                return None
            if comm.is_instrument_connected():
                self.LogMessage(u"第%s次检查信号状态：已连接" % i)
                self.status.SetBitmap(Picture.status_connect1)
                self.message.SetLabel(u"信号发生器已连接，测试中")
                return True
            else:
                self.LogMessage(u"第%s次检查信号状态：未连接" % i)
                self.message.SetLabel(u"正在连接信号发生器")
                self.status.SetBitmap(Picture.status_disconnect)
                comm.hold_baseband()
                self.status.SetBitmap(wx.NullBitmap)
                comm.release_baseband()
        return False

    def test_block_error_count(self):
        block_lst = list()
        for i in range(40):
            for _ in range(20):
                if self.stop_flag:
                    return None
                self.Sleep(0.05)
            self.update_bler(block_lst)
            self.panel_mpl.refresh(slot=block_lst)
            self.LogMessage(u"当前误块数[%s]" % block_lst[-1])
            if len(block_lst) >= 5 and block_lst[-5:] == [0, 0, 0, 0, 0]:
                self.LogMessage(u"误块数测试通过")
                return True
            if block_lst.count(0) >= 10:
                self.LogMessage(u"误块数测试通过")
                return True
        self.LogMessage(u"误块数测试失败")
        return False

    def test_signal_intensity(self):
        signal_sources = self.GetSignalSources()
        signal_sources.SetPower(50)
        for _ in range(25):
            if self.stop_flag:
                return None
            self.Sleep(0.05)
        rssi0, rssi1 = self.update_rssi()
        self.LogMessage(u"当前天线0信号强度[%s]" % rssi0)
        self.LogMessage(u"当前天线1信号强度[%s]" % rssi1)
        if abs(rssi0 - rssi1) <= 8:
            self.LogMessage(u"信号强度测试通过")
            return True
        self.LogMessage(u"信号强度测试失败")
        return False

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_communicate()
            uart.hold_baseband()
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
        finally:
            obj.Enable()

    def update_bler(self, lst):
        comm = self.get_communicate()
        result = comm.get_rssi_and_bler()
        if result is not None and int(result, 16) > 0:
            bler = int(result[8:], 16)
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            lst.append(bler)
            self.rssi_0.SetValue(str(rssi0))
            self.rssi_1.SetValue(str(rssi1))
        else:
            self.update_bler(lst=lst)

    def update_rssi(self):
        comm = self.get_communicate()
        result = comm.get_rssi_and_bler()
        if result is not None and int(result, 16) > 0:
            rssi0 = int(result[0:4], 16) - 65536
            rssi1 = int(result[4:8], 16) - 65536
            self.rssi_0.SetValue(str(rssi0))
            self.rssi_1.SetValue(str(rssi1))
            return rssi0, rssi1
        else:
            return self.update_rssi()


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
        self.y_max = 130
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
        self.Axes.legend()
