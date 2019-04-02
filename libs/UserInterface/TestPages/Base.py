# -*- encoding:UTF-8 -*-
import wx
import logging
from libs.Config import Color
from libs.Config import Font
from libs.Config import Path
from libs import Utility
import os
import time
import threading

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
        with open(os.path.join(Path.LOG_SAVE, "%s.log" % comm.SerialNumber), 'a') as log:
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

        self.__parent = parent
        self.__result_controls = list()
        self.name = name
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize,
                              wx.ALIGN_CENTER | wx.SIMPLE_BORDER)
        title.SetFont(Font.TEST_TITLE)
        title.SetBackgroundColour(Color.LightYellow1)
        self.main_sizer.Add(title, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.main_sizer.Add(self.__init_result_sizer(), 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(self.main_sizer)
        self.Layout()

    def __init_result_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__init_device_info(), 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.__init_case_result_sizer(), 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.__init_operation_sizer(), 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM | wx.ALL, 0)
        return sizer

    def __init_device_info(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "设备信息"), wx.VERTICAL)
        row0 = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                         wx.TE_READONLY | wx.NO_BORDER)
        self.serial_number.SetBackgroundColour(Color.gray81)
        title.SetFont(Font.COMMON_1)
        self.serial_number.SetFont(Font.COMMON_1_LARGE)
        row0.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        row0.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        sizer.Add(row0, 0, wx.EXPAND | wx.LEFT, 10)
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

    def __init_operation_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        upload = wx.Button(self, wx.ID_ANY, u"TODO:上传测试结果", wx.DefaultPosition, (-1, 40), 0, name="upload_result")
        refresh = wx.Button(self, wx.ID_ANY, u"刷新结果", wx.DefaultPosition, (-1, 40), 0, name="refresh_result")
        screenshot = wx.Button(self, wx.ID_ANY, u"保存截图", wx.DefaultPosition, (-1, 40), 0, name="screenshot")
        upload.Bind(wx.EVT_BUTTON, self.__on_button_click)
        refresh.Bind(wx.EVT_BUTTON, self.__on_button_click)
        screenshot.Bind(wx.EVT_BUTTON, self.__on_button_click)
        sizer.Add(upload, 0, wx.ALL, 5)
        sizer.Add(refresh, 0, wx.ALL, 5)
        sizer.Add(screenshot, 0, wx.ALL, 5)
        return sizer

    def __on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "refresh_result":
            Utility.append_thread(target=self.__update_color_based_on_result)
        elif name == "upload_result":
            Utility.Alert.Info("Hello World!")
        elif name == "screenshot":
            self.capture_screen()
        else:
            Utility.Alert.Error("Hello WUYOU!")

    def get_name(self):
        return self.name

    def capture_screen(self):
        default_name = "%s.png" % self.serial_number.GetValue()
        dlg = wx.FileDialog(self, "保存截图", "", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                            wildcard="Screenshots(*.png)|*.png|All files(*.*)|*.*",
                            defaultFile=default_name)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:  # 如果没有文件名后缀
                filename = filename + '.png'
        else:
            filename = None
        dlg.Destroy()
        time.sleep(1)
        if filename is not None:
            screen = wx.ScreenDC()
            size, pos = self.GetSize(), self.GetScreenPosition()
            width, height = size[0], size[1]
            x, y = pos[0], pos[1]
            bmp = wx.Bitmap(width, height)
            memory = wx.MemoryDC(bmp)
            memory.Blit(0, 0, width, height, screen, x, y)
            bmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)

    def Show(self):
        super(ReportPage, self).Show()
        self.__parent.refresh()
        Utility.append_thread(target=self.__update_color_based_on_result)

    def Hide(self):
        super(ReportPage, self).Hide()
        self.__parent.refresh()

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
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, t), wx.VERTICAL)
        for row in rows:
            row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for ctrl in row:
                row_sizer.Add(ctrl, 0, wx.ALL, 3)
            sizer.Add(row_sizer, 0, wx.EXPAND | wx.ALL, 5)
        return sizer

    def __init_result_ctrl(self, flag, name):
        title = StaticText(parent=self, flag=flag, name=name)
        self.__result_controls.append(title)
        return title

    def __update_color_based_on_result(self):
        self.__set_result_color_as_default()
        socket = Variable.get_socket()
        self.serial_number.SetValue(socket.get_serial_number())
        results = socket.get_all_flag_results()
        if results is not None:
            for ctrl in self.__result_controls:
                result = results[ctrl.GetFlag() - 1]
                ctrl.SetResult(result)
        else:
            for ctrl in self.__result_controls:
                result = socket.get_flag_result(ctrl.GetFlag())
                ctrl.SetResult(result)

    def __set_result_color_as_default(self):
        self.serial_number.SetValue("")
        for ctrl in self.__result_controls:
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
