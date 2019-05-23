# -*- encoding:UTF-8 -*-
import logging
import os
import threading
import time

import wx

from libs import Utility
from libs.Config import Color
from libs.Config import Font
from libs.Config import Path

logger = logging.getLogger(__name__)
result2value = {
    "NotTest": "1",
    "PASS": "2",
    "FAIL": "3",
}
value2result = {
    "1": "NotTest",
    "2": "PASS",
    "3": "FAIL",
}
type2name = {
    "RF": u"射频测试",
    "PCBA": u"PCBA测试",
    "整机": u"组装测试",
}


class Variable(object):
    __uart = None
    __socket = None

    @classmethod
    def get_uart(cls):
        return cls.__uart

    @classmethod
    def set_uart(cls, uart=None):
        cls.__uart = uart
        return True

    @classmethod
    def get_socket(cls):
        return cls.__socket

    @classmethod
    def set_socket(cls, socket=None):
        cls.__socket = socket
        return True


class TestPage(wx.Panel):
    def __init__(self, parent, type):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.AUTO = False
        self.lock = threading.Lock()
        self.type = type
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, self.get_name(), wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        test_sizer = self.init_test_sizer()
        result_sizer = self.init_result_sizer()
        self.main_sizer.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.main_sizer.Add(test_sizer, 1, wx.EXPAND | wx.ALL, 1)
        self.main_sizer.Add(result_sizer, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()

    def init_test_sizer(self):
        raise NotImplementedError

    def init_result_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.PassButton = self.create_result_button(True)
        self.FailButton = self.create_result_button(False)
        sizer.Add(self.PassButton, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.FailButton, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    @staticmethod
    def get_communicate():
        return Variable.get_socket()

    def get_result(self):
        comm = self.get_communicate()
        return comm.get_flag_result(self.get_flag())

    def get_type(self):
        return self.type

    def get_name(self):
        return self.GetName()

    @staticmethod
    def GetName():
        raise NotImplementedError

    def get_flag(self):
        return self.GetFlag(t=self.type)

    @staticmethod
    def GetFlag(t):
        raise NotImplementedError

    def Show(self):
        super(TestPage, self).Show()
        self.__parent.refresh()
        self.before_test()
        self.start_test()

    def Hide(self):
        super(TestPage, self).Hide()
        self.__parent.refresh()
        self.stop_test()

    def create_result_button(self, isPass):
        color = Color.SpringGreen3 if isPass else Color.Firebrick2
        label = u"PASS" if isPass else u"FAIL"
        button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0, name=label)
        button.SetBackgroundColour(color)
        button.SetFont(Font.COMMON_1_LARGE_BOLD)
        button.Bind(wx.EVT_BUTTON, self.on_result_button)
        return button

    def on_result_button(self, event):
        obj = event.GetEventObject()
        self.SetResult(obj.Name)

    def before_test(self):
        self.EnablePass(enable=False)

    def start_test(self):
        print 'start_test'

    def stop_test(self):
        print 'stop_test'

    def SetResult(self, result):
        logger.debug("\"%s\" Result is : <%s>" % (self.get_name(), result))
        self.FormatPrint(result, symbol="=")
        uart = self.get_communicate()
        if uart.set_flag_result(flag=self.get_flag(), result=result2value[result]):
            self.__parent.next_page()

    def EnablePass(self, enable=True):
        if enable and self.AUTO:
            self.SetResult("PASS")
        else:
            self.PassButton.Enable(enable=enable)

    def LogMessage(self, msg):
        msg = msg.strip('\r\n')
        comm = self.get_communicate()
        if comm is None:
            return
        with open(os.path.join(Path.TEST_LOG_SAVE, "%s.log" % comm.SerialNumber), 'a') as log:
            log.write(u"{time}:{message}\n".format(time=Utility.get_timestamp(), message=msg))

    @staticmethod
    def Sleep(secs):
        time.sleep(secs)

    def FormatPrint(self, info, symbol="*", length=50):
        if self.lock.acquire():
            try:
                body = " %s: %s" % (self.get_name(), info)
                self.LogMessage(symbol * length)
                self.LogMessage(symbol + body)
                self.LogMessage(symbol * length)
            finally:
                self.lock.release()


class ReportPage(wx.Panel):
    def __init__(self, parent, name=u"测试总结"):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.result_controls = list()
        self.name = name
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.init_title_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        self.main_sizer.Add(self.init_result_sizer(), 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()

    def init_title_sizer(self):
        size = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, self.name, wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        size.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        return size

    def init_result_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_case_result_sizer(), 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.init_operation_sizer(), 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM | wx.ALL, 0)
        return sizer

    def __init_case_result_sizer(self):
        from libs.Config.Cases import RF_CASES
        from libs.Config.Cases import PCBA_CASES
        from libs.Config.Cases import MACHINE_CASES
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_result_ctrl_sizer(cases=RF_CASES, t="RF", gap=3), 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.__init_result_ctrl_sizer(cases=PCBA_CASES, t="PCBA", gap=5), 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.__init_result_ctrl_sizer(cases=MACHINE_CASES, t="整机", gap=5), 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def init_operation_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        return sizer

    def get_name(self):
        return self.name

    def Show(self):
        super(ReportPage, self).Show()
        self.parent.refresh()
        Utility.append_thread(target=self.update_color_based_on_result)

    def Hide(self):
        super(ReportPage, self).Hide()
        self.parent.refresh()

    def get_result(self):
        return "Report"

    def __init_result_ctrl_sizer(self, cases, t, gap=3):
        def split_cases():
            lst = list()
            for case in cases:
                flag = case.GetFlag(t=t)
                name = case.GetName()
                wx_control = self.__init_result_ctrl(flag=flag, name=name)
                lst.append(wx_control)
            split_lst = [lst[i:i + gap] for i in range(0, len(lst), gap)]
            return split_lst

        rows = split_cases()

        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, type2name[t]), wx.VERTICAL)
        for row in rows:
            row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for ctrl in row:
                row_sizer.Add(ctrl, 0, wx.ALL, 3)
            sizer.Add(row_sizer, 0, wx.EXPAND | wx.ALL, 5)
        return sizer

    def __init_result_ctrl(self, flag, name):
        title = StaticText(parent=self, flag=flag, name=name)
        self.result_controls.append(title)
        return title

    def update_color_based_on_result(self):
        self.set_result_color_as_default()
        socket = Variable.get_socket()
        results = socket.get_all_flag_results()
        if results is not None:
            for ctrl in self.result_controls:
                result = results[ctrl.GetFlag() - 1]
                ctrl.SetResult(result)
        else:
            for ctrl in self.result_controls:
                result = socket.get_flag_result(ctrl.GetFlag())
                ctrl.SetResult(result)

    def set_result_color_as_default(self):
        for ctrl in self.result_controls:
            ctrl.SetResult("NotTest")


class StaticText(wx.StaticText):
    def __init__(self, parent, name, flag):
        wx.StaticText.__init__(self, parent, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize,
                               wx.TEXT_ALIGNMENT_CENTRE | wx.SIMPLE_BORDER)
        self.SetFont(Font.REPORT_LARGE)
        # print "%s  %s" % (name, flag)
        self.__name = name
        self.__flag = flag
        self.__result = ""
        self.__color = {
            "True": Color.GoogleGreen,
            "False": Color.GoogleRed,
            "NotTest": Color.gray81,
        }
        self.SetResult("NotTest")

    def GetName(self):
        return self.__name

    def GetResult(self):
        return self.__result

    def GetFlag(self):
        return self.__flag

    def SetResult(self, result):
        if result in ["NotTest", "1"]:
            self.__result = "NotTest"
        elif result in ["True", "2"]:
            self.__result = "True"
        elif result in ["False", "3"]:
            self.__result = "False"
        else:
            self.__result = "NotTest"
            logger.error("Wrong Result Type: %s" % result)
        self.SetBackgroundColour(self.__color[self.__result])
        self.Refresh()


class RF_ConfigPage(wx.Panel):
    def __init__(self, parent, name=u"射频配置"):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.__parent = parent
        self.__recv_lst = list()
        self.__tran_lst = list()
        self.name = name
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        self.main_sizer.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.main_sizer.Add(self.__init_configuration_sizer(), 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.EnableConfig(enable=False)

    def __init_configuration_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_receiver_sizer(), 0, wx.EXPAND, 5)
        sizer.Add(self.__init_transmit_sizer(), 0, wx.EXPAND, 5)
        sizer.Add(self.__init_operation_sizer(), 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        return sizer

    def create_attr_value_sizer(self, label, attr_name, attr_value):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        name = wx.StaticText(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        value = wx.TextCtrl(self, wx.ID_ANY, attr_value, wx.DefaultPosition, wx.DefaultSize, 0, name=attr_name)
        sizer.Add(name, 0, wx.EXPAND | wx.TOP, 4)
        sizer.Add(value, 1, wx.EXPAND | wx.ALL, 2)
        return sizer, value

    def create_min_max_sizer(self, freq, cfg):
        def create_unit_size(name):
            unit_sizer = wx.BoxSizer(wx.HORIZONTAL)
            min_string = "%s(min)" % name
            max_string = "%s(max)" % name
            name = wx.StaticText(self, wx.ID_ANY, u"%s路 判定范围: " % name.upper(), wx.DefaultPosition, wx.DefaultSize,
                                 wx.ALIGN_CENTER)
            wavy = wx.StaticText(self, wx.ID_ANY, u"～", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
            min = wx.TextCtrl(self, wx.ID_ANY, cfg[min_string], wx.DefaultPosition, (40, -1), wx.TE_CENTER,
                              name=min_string)
            max = wx.TextCtrl(self, wx.ID_ANY, cfg[max_string], wx.DefaultPosition, (40, -1), wx.TE_CENTER,
                              name=max_string)
            self.__tran_lst.append(min)
            self.__tran_lst.append(max)
            unit_sizer.Add(name, 0, wx.TOP, 4)
            unit_sizer.Add(min, 0, wx.ALL, 1)
            unit_sizer.Add(wavy, 0, wx.TOP, 4)
            unit_sizer.Add(max, 0, wx.ALL, 1)
            return unit_sizer

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(create_unit_size(name="%sa" % freq), 0, wx.EXPAND, 0)
        sizer.Add(create_unit_size(name="%sb" % freq), 0, wx.EXPAND, 0)
        return sizer

    def __init_receiver_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "接收灵敏度设置"), wx.VERTICAL)
        row_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalSources")
        power_2400, self.power_2400 = self.create_attr_value_sizer("2.4G信号源功率: ", attr_name="2400power",
                                                                   attr_value=config["2400power"])
        power_5800, self.power_5800 = self.create_attr_value_sizer("5.8G信号源功率: ", attr_name="5800power",
                                                                   attr_value=config["5800power"])
        wave_file, self.wave_file = self.create_attr_value_sizer("波形文件: ", attr_name="wave_file",
                                                                 attr_value=config["wave_file"])
        self.__recv_lst.append(self.power_2400)
        self.__recv_lst.append(self.power_5800)
        self.__recv_lst.append(self.wave_file)

        row_sizer1.Add(power_2400, 0, wx.EXPAND | wx.ALL, 5)
        row_sizer1.Add(power_5800, 0, wx.EXPAND | wx.ALL, 5)
        row_sizer1.Add(wave_file, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(row_sizer1, 1, wx.EXPAND, 0)
        return sizer

    def __init_transmit_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "发射功率设置"), wx.VERTICAL)
        # row_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # row_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer")
        # for freq in [2410, 2450, 2475]:
        #     row_sizer1.Add(self.create_min_max_sizer(freq=freq, cfg=config), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        # for freq in [5750, 5800, 5850]:
        #     row_sizer2.Add(self.create_min_max_sizer(freq=freq, cfg=config), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        ref_level, self.ref_level = self.create_attr_value_sizer("功率参考值: ", attr_name="ref_level",
                                                                 attr_value=config["ref_level"])
        thr_level, self.thr_level = self.create_attr_value_sizer("功率阀值: ", attr_name="thr_level",
                                                                 attr_value=config["thr_level"])
        gain24, self.gain24 = self.create_attr_value_sizer("2.4G线损设置: ", attr_name="2400gain", attr_value=config["2400gain"])
        gain58, self.gain58 = self.create_attr_value_sizer("5.8G线损设置: ", attr_name="5800gain", attr_value=config["5800gain"])
        self.__tran_lst.append(self.ref_level)
        self.__tran_lst.append(self.thr_level)
        self.__tran_lst.append(self.gain24)
        self.__tran_lst.append(self.gain58)
        row_sizer3.Add(ref_level, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        row_sizer3.Add(thr_level, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        row_sizer3.Add(gain24, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        row_sizer3.Add(gain58, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        # sizer.Add(row_sizer1, 0, wx.EXPAND, 0)
        # sizer.Add(row_sizer2, 0, wx.EXPAND, 0)
        sizer.Add(row_sizer3, 0, wx.EXPAND, 0)
        return sizer

    def __init_operation_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.unlock = wx.Button(self, wx.ID_ANY, u"解锁", wx.DefaultPosition, (-1, 40), 0, name="unlock")
        self.lock = wx.Button(self, wx.ID_ANY, u"锁定", wx.DefaultPosition, (-1, 40), 0, name="lock")
        self.save = wx.Button(self, wx.ID_ANY, u"保存", wx.DefaultPosition, (-1, 40), 0, name="save")
        self.unlock.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.lock.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.save.Bind(wx.EVT_BUTTON, self.on_button_click)
        sizer.Add(self.unlock, 0, wx.ALL, 5)
        sizer.Add(self.lock, 0, wx.ALL, 5)
        sizer.Add(self.save, 0, wx.ALL, 5)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "unlock":
            dlg = wx.TextEntryDialog(self, u'请输入解锁码:', u'解锁配置', style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.GetValue() in ["13641746250", "13636359582", "15921863784"]:
                    self.EnableConfig(True)
                else:
                    Utility.Alert.Error(u"解锁码错误")
        elif name == "lock":
            self.EnableConfig(False)
        elif name == "save":
            self.SaveConfig()
            self.EnableConfig(False)

    def get_name(self):
        return self.name

    def Show(self):
        super(RF_ConfigPage, self).Show()
        self.__parent.refresh()

    def Hide(self):
        super(RF_ConfigPage, self).Hide()
        self.__parent.refresh()

    def get_result(self):
        return "Report"

    def EnableConfig(self, enable):
        for ctrl in self.__recv_lst:
            ctrl.Enable(enable=enable)
        for ctrl in self.__tran_lst:
            ctrl.Enable(enable=enable)
        self.unlock.Enable(enable=not enable)
        self.lock.Enable(enable=enable)
        self.save.Enable(enable=enable)

    def SaveConfig(self):
        recv_data = dict()
        tran_data = dict()
        for ctrl in self.__recv_lst:
            recv_data[ctrl.GetName()] = ctrl.GetValue()
        for ctrl in self.__tran_lst:
            tran_data[ctrl.GetName()] = ctrl.GetValue()
        data = {
            "SignalAnalyzer": tran_data,
            "SignalSources": recv_data,
        }
        Utility.ParseConfig.modify(Path.CONFIG, data=data)
