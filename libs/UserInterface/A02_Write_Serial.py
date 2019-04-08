# -*- encoding:UTF-8 -*-
import wx
import logging
import sys
from socket import timeout as SocketTimeout
from socket import error as SocketError
from libs.Config import Color
from libs.Utility import Socket
from libs import Utility
logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"写序列号", size=(600, 150),
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.panel = Panel(self)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.socket = None
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        device_sizer = self.__init_device_sizer()
        self.btn_write_sn = wx.Button(self, wx.ID_ANY, u"写  入", wx.DefaultPosition, (-1, 50), style=0,
                                      name='set_sn')
        self.btn_write_sn.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.btn_write_sn.SetFont(wx.Font(23, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        main_sizer.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.btn_write_sn, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Enable(False)

    def __init_device_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__init_serial_number_sizer(), 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.__init_button_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_button_sizer(self):
        size = (40, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        pic_connect = wx.Image('resource/icon/Connect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        pic_disconnect = wx.Image('resource/icon/Disconnect.ico', wx.BITMAP_TYPE_ICO).ConvertToBitmap()
        self.btn_connect = wx.BitmapButton(self, wx.ID_ANY, pic_connect, wx.DefaultPosition, size, style=0,
                                           name='connect')
        self.btn_disconnect = wx.BitmapButton(self, wx.ID_ANY, pic_disconnect, wx.DefaultPosition, size, style=0,
                                              name='disconnect')

        self.btn_connect.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.btn_disconnect.Bind(wx.EVT_BUTTON, self.on_button_click)
        sizer.Add(self.btn_connect, 0, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.btn_disconnect, 0, wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_serial_number_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                         wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.serial_number.Bind(wx.EVT_SET_FOCUS, self.click_on_text_ctrl)
        f = wx.Font(23, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.title.SetFont(f)
        self.serial_number.SetFont(f)
        sizer.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP | wx.LEFT, 5)
        sizer.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        # if name == "refresh":
        #     self.port_choice.SetItems(UART.list_ports())
        if name == "connect":
            self.connect()
        elif name == "disconnect":
            self.disconnect()
        elif name == "set_sn":
            self.set_serial_number()

    def connect(self):
        if self.socket is not None:
            self.socket.close()
        try:
            self.socket = Socket.Client(address="192.168.1.1")
            self.socket.get_serial_number()
            self.refresh_serial_number()
            self.Enable(enable=True)
        except SocketError:
            Utility.Alert.Error(u"连接失败：超时。")
            return False
        except SocketTimeout:
            Utility.Alert.Error(u"连接失败：超时。")
            return False
        except IndexError:
            Utility.Alert.Error(u"连接失败：目标拒绝。")
            return False
        except KeyError:
            Utility.Alert.Error(u"连接失败：目标拒绝。")
            self.socket.close()
            self.socket = None
            return False

    def disconnect(self):
        if self.socket is not None:
            self.socket.close()
        self.socket = None
        self.Layout()
        self.Enable(False)
        self.serial_number.SetValue("")

    def set_serial_number(self):
        serial = self.serial_number.GetValue()
        if not serial:
            Utility.Alert.Error(u"请输入序列号")
            return
        elif len(serial) > 18:
            Utility.Alert.Error(u"输入的序列号太长，\n当前：%s，最大：18" % len(serial))
            return
        result = self.socket.get_serial_number()
        if result is None:
            Utility.Alert.Error("通讯异常，请重新连接。")
            self.disconnect()
            return False
        if result != "123456789012345678":
            dlg = wx.MessageDialog(
                None,
                u"设备中已存在序列号：\"%s\"，\n是否要用新的序列号：\"%s\" 替换。" % (result, serial),
                u"消息",
                wx.YES_NO | wx.ICON_QUESTION
            )
            if dlg.ShowModal() == wx.ID_YES:
                self.update_serial_number(serial=serial)
            dlg.Destroy()
            return
        self.update_serial_number(serial=serial)

    def refresh_serial_number(self):
        value = self.socket.get_serial_number()
        if value is None:
            raise KeyError
        elif value == "123456789012345678":
            self.serial_number.SetValue(value="")
        else:
            self.serial_number.SetValue(value=value)

    def update_serial_number(self, serial):
        for x in range(3):
            self.socket.set_serial_number(serial)
            result = self.socket.get_serial_number()
            if serial == result:
                dialog = Utility.Alert.CountdownDialog(u"写入成功，3秒后自动关闭。")
                dialog.Countdown(countdown=3)
                self.disconnect()
                return True
        Utility.Alert.Error(u"写入失败，请重试。")
        self.refresh_serial_number()
        return False

    def Enable(self, enable=True):
        lst1 = [self.btn_disconnect, self.serial_number, self.btn_write_sn]
        lst2 = [self.btn_connect]
        for ctrl in lst1:
            ctrl.Enable(enable)
        for ctrl in lst2:
            ctrl.Enable(not enable)
        if enable:
            if self.serial_number.GetValue() == "":
                self.serial_number.SetFocus()
            else:
                self.title.SetFocus()

    def click_on_text_ctrl(self, event):
        self.serial_number.SetValue("")
        event.Skip()
