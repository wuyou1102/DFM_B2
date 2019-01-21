# -*- encoding:UTF-8 -*-
import logging
import matplotlib
import wx
import Base
from libs import Utility
from libs.Config import String
from libs.Config import Picture

matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy

logger = logging.getLogger(__name__)


class ReceiveBase(Base.Page):
    def __init__(self, parent, type, freq=5100):
        self.freq = freq
        Base.Page.__init__(self, parent=parent, name="接收测试", type=type)
        self.init_variable()

    def init_test_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.__init_freq_point_sizer(), 1, wx.EXPAND, 0)
        # hori_sizer.Add(self.__init_mcs_sizer(), 1, wx.EXPAND, 0)
        hori_sizer.Add(self.__init_status_sizer(), 0, wx.EXPAND | wx.ALIGN_RIGHT, 0)
        sizer.Add(hori_sizer, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.__init_mpl_sizer(), 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_mpl_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_mpl = BlerMpl(self)
        sizer.Add(self.panel_mpl, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_freq_point_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"当前频点: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.current_point = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        sizer.Add(self.current_point, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        p = str(self.freq)
        button = wx.Button(self, wx.ID_ANY, p, wx.DefaultPosition, (40, -1), 0, name=p)
        button.Bind(wx.EVT_BUTTON, self.on_freq_point_selected)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        return sizer

    def on_freq_point_selected(self, event):
        obj = event.GetEventObject()
        uart = self.get_uart()
        uart.set_frequency_point(obj.Name + "000")
        self.update_current_freq_point()

    def on_mcs_selected(self, event):
        obj = event.GetEventObject()
        selected = obj.GetSelection()
        uart = self.get_uart()
        uart.set_qam(value=selected)
        self.update_current_mcs()

    def __init_status_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status = wx.StaticBitmap(self, wx.ID_ANY, Picture.status_disconnect, wx.DefaultPosition, (33, 33), 0)
        restart = wx.BitmapButton(self, wx.ID_ANY, Picture.restart, wx.DefaultPosition, (33, 33), 0)
        restart.Bind(wx.EVT_BUTTON, self.on_restart)
        sizer.Add(restart, 0, wx.ALL, 1)
        sizer.Add(self.status, 0, wx.ALL, 1)
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
            uart = self.get_uart()
            value = uart.get_frequency_point()
            self.current_point.SetValue(Utility.convert_freq_point(value=value))

        Utility.append_thread(target=update_freq)

    def update_current_mcs(self):
        def update_mcs():
            uart = self.get_uart()
            value = uart.get_qam()
            self.current_mcs.SetSelection(int(value, 16))

        Utility.append_thread(target=update_mcs)

    def before_test(self):
        self.init_variable()
        self.panel_mpl.init_axes()
        uart = self.get_uart()
        uart.set_rx_mode_20m()
        self.update_current_freq_point()
        self.update_current_mcs()

    def init_variable(self):
        self.stop_flag = True
        self.slot = []
        # self.br = []

    def start_test(self):
        self.FormatPrint(info="Started")
        Utility.append_thread(target=self.draw_line)
        Utility.append_thread(target=self.refresh_status)

    def stop_test(self):
        self.stop_flag = False

    def append_log(self, msg):
        self.LogMessage(msg)
        wx.CallAfter(self.output.AppendText, u"{time}\t{message}\n".format(time=Utility.get_time(), message=msg))

    def get_flag(self):
        return String.RF_RECEIVE

    def draw_line(self):
        while self.stop_flag:
            self.update_bler()
            self.panel_mpl.refresh(self.slot, self.br)
            self.Sleep(1)

    def on_restart(self, event):
        obj = event.GetEventObject()
        try:
            obj.Disable()
            uart = self.get_uart()
            uart.hold_baseband()
            self.Sleep(1)
            uart.release_baseband()
            Utility.Alert.Info(u"基带重启完成")
        finally:
            obj.Enable()

    def refresh_status(self):
        def set_bitmap(bitmap):
            self.status.SetBitmap(bitmap)
            self.Sleep(0.577)

        def set_as_disconnect():
            set_bitmap(Picture.status_disconnect)
            set_bitmap(wx.NullBitmap)

        def set_as_connect():
            set_bitmap(Picture.status_connect1)
            set_bitmap(Picture.status_connect2)

        uart = self.get_uart()
        while self.stop_flag:
            if uart.is_instrument_connected():
                set_as_connect()
            else:
                set_as_disconnect()

    def update_bler(self):
        uart = self.get_uart()
        self.slot.append(self.get_bler(uart.get_slot_bler))
        # self.br.append(self.get_bler(uart.get_br_bler))

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
        self.data_limit_length = 120
        self.y_max = 100
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

    # def on_save(self, event):
    #     dlg = wx.FileDialog(
    #         self,
    #         message="Save plot as...",
    #         defaultDir=os.getcwd(),
    #         defaultFile="%s-%s.png" % (self.get_title(), Utility.get_timestamp()),
    #         wildcard="PNG (*.png)|*.png",
    #         style=wx.FD_SAVE)
    #
    #     if dlg.ShowModal() == wx.ID_OK:
    #         path = dlg.GetPath()
    #         self.FigureCanvas.print_figure(path, dpi=self.dpi)

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

    def init_axes(self, x_lower=0, x_upper=120):
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
