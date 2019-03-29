# -*- encoding:UTF-8 -*-
import wx
from libs.Utility.Timeout import Timeout
import logging
import sys
from libs.Config import Path
from libs.Config import Color
from libs.Config import Font
from libs.Utility import Socket
from libs import Utility
from libs.Utility.B2 import WebSever
import vlc
import threading
import requests
import time

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


def import_scapy():
    from scapy.layers.inet import Ether
    from scapy.sendrecv import sendp


import_thread = Utility.append_thread(target=import_scapy)


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"图传测试", size=(800, 700),
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.panel = Panel(self)
        self.SetBackgroundColour(Color.Azure2)
        self.Center()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.socket = None
        self.stop = False
        self.test_thread = None
        self.web = WebSever("192.168.1.1")
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        device_sizer = self.__init_device_sizer()

        test_sizer = wx.BoxSizer(wx.HORIZONTAL)
        test_sizer.Add(self.__init_config_sizer(), 0, wx.EXPAND | wx.ALL, 5)
        test_sizer.Add(self.__init_previewer_sizer(), 1, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(test_sizer, 1, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(self.__init_message_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(self.__init_result_sizer(), 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Enable(False)
        self.__instance = vlc.Instance()
        self.__player = self.__instance.media_player_new()
        self.__player.set_hwnd(self.preview.GetHandle())
        self.__player.set_media(self.__instance.media_new(self.GetUrl()))
        self.__player.play()
        Utility.append_thread(target=self.printss)

    def printss(self):
        import time
        while True:
            print self.__player.get_state()
            if self.__player.get_state() == vlc.State.Ended:
                self.__player.stop()
            elif self.__player.get_state() == vlc.State.Stopped:
                self.__player.play()
            print self.socket.get_rssi_and_bler()
            time.sleep(0.5)

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

    def __init_previewer_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.preview = wx.Panel(self, wx.ID_ANY)
        self.preview.SetBackgroundColour(wx.BLACK)
        sizer.Add(self.preview, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_config_sizer(self):
        def create_text_ctrl(title, value, hide=False):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(self, wx.ID_ANY, title, wx.DefaultPosition, wx.DefaultSize, 0)
            title.SetFont(Font.COMMON_1)
            value = wx.TextCtrl(self, wx.ID_ANY, value, wx.DefaultPosition, wx.DefaultSize, 0)
            value.SetFont(Font.COMMON_1)
            if hide:
                title.Hide()
                value.Hide()
            sizer.Add(title, 0, wx.EXPAND | wx.TOP, 4)
            sizer.Add(value, 1, wx.EXPAND | wx.ALL, 1)
            return sizer, value

        def create_button(label, name):
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0, name=name)
            button.Bind(wx.EVT_BUTTON, self.on_button_click)
            return button

        sizer = wx.BoxSizer(wx.VERTICAL)
        config = self.__get_config(name="rtsp")
        address_sizer, self.address = create_text_ctrl(u"地  址: ", config.get("address", "192.168.1.2"))
        port_sizer, self.port = create_text_ctrl(u"端口号: ", config.get("port", "554"), hide=True)
        username_sizer, self.username = create_text_ctrl(u"用户名: ", config.get("username", "admin"), hide=True)
        password_sizer, self.password = create_text_ctrl(u"密  码: ", config.get("password", "Password01!"), hide=True)
        network_id_sizer, self.network_id = create_text_ctrl(u"网络ID: ", config.get("id", "666!"))
        self.btn_save = create_button(label=u"保存设置", name="save")
        self.btn_start = create_button(label=u"开始测试", name="start")
        sizer.Add(address_sizer, 0, wx.EXPAND, 1)
        # sizer.Add(port_sizer, 0, wx.EXPAND, 1)
        # sizer.Add(username_sizer, 0, wx.EXPAND, 1)
        # sizer.Add(password_sizer, 0, wx.EXPAND, 1)
        sizer.Add(network_id_sizer, 0, wx.EXPAND, 1)
        sizer.Add(self.btn_save, 0, wx.EXPAND, 1)
        sizer.Add(self.btn_start, 0, wx.EXPAND, 1)
        return sizer

    def __init_message_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.message = wx.StaticText(self, wx.ID_ANY, u"今天天气真好", wx.DefaultPosition, wx.DefaultSize, 0)
        self.message.SetFont(wx.Font(40, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.message.SetBackgroundColour(Color.DarkTurquoise)
        sizer.Add(self.message, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        return sizer

    def __get_config(self, name):
        return Utility.ParseConfig.get(path=Path.CONFIG, section=name)

    def __init_serial_number_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self, wx.ID_ANY, u"序列号: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.serial_number = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                         wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        f = wx.Font(23, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.title.SetFont(f)
        self.serial_number.SetFont(f)
        sizer.Add(self.title, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP | wx.LEFT, 5)
        sizer.Add(self.serial_number, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, 1)
        return sizer

    def __init_result_sizer(self):
        def create_result_button(isPass):
            color = Color.SpringGreen3 if isPass else Color.Firebrick2
            label = u"PASS" if isPass else u"FAIL"
            button = wx.Button(self, wx.ID_ANY, label, wx.DefaultPosition, (-1, 40), 0, name=label)
            button.SetBackgroundColour(color)
            button.SetFont(Font.COMMON_1_LARGE_BOLD)
            button.Bind(wx.EVT_BUTTON, self.on_button_click)
            return button

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_pass = create_result_button(True)
        self.btn_fail = create_result_button(False)
        sizer.Add(self.btn_pass, 1, wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.btn_fail, 1, wx.EXPAND | wx.ALL, 1)
        return sizer

    def on_button_click(self, event):
        obj = event.GetEventObject()
        name = obj.Name
        if name == "connect":
            self.connect()
        elif name == "disconnect":
            self.disconnect()
        elif name == "save":
            self.save_config()
        elif name == "start":
            self.start_test()
        elif name in ["PASS", "FAIL"]:
            print name

    def connect(self):
        if self.socket is not None:
            self.socket.close()
        try:
            self.socket = Socket.Client(address="192.168.1.1")
            self.refresh_serial_number()
            self.socket.unload_protocol_stack()
            self.Enable(enable=True)
        except Timeout:
            Utility.Alert.Error(u"连接失败：超时。")
            return False
        except IndexError:
            Utility.Alert.Error(u"连接失败：目标拒绝。")
            return False
        except KeyError:
            Utility.Alert.Error(u"设备没有有效的序列号，无法测试。请返回上一步完成写号后继续")
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

    def save_config(self):
        data = dict()
        data["address"] = self.address.GetValue()
        data["port"] = self.port.GetValue()
        data["username"] = self.username.GetValue()
        data["password"] = self.password.GetValue()
        data["id"] = self.network_id.GetValue()
        Utility.ParseConfig.modify(path=Path.CONFIG, data={"rtsp": data})

    def start_test(self):
        if self.test_thread is not None:
            self.test_thread.stop()
        self.test_thread = TestThread(self)
        self.test_thread.setDaemon(True)
        self.test_thread.start()

    def refresh_serial_number(self):
        value = self.socket.get_serial_number()
        if value is None:
            raise KeyError
        elif value == "123456789012345678":
            raise KeyError
        else:
            self.serial_number.SetValue(value=value)

    def Enable(self, enable=True):
        lst1 = [self.btn_disconnect, self.serial_number, self.btn_start]
        lst2 = [self.btn_connect]
        for ctrl in lst1:
            ctrl.Enable(enable)
        for ctrl in lst2:
            ctrl.Enable(not enable)

    def GetUrl(self):
        return "rtsp://{username}:{password}@{address}:{port}".format(
            username=self.username.GetValue(),
            password=self.password.GetValue(),
            port=self.port.GetValue(),
            address=self.address.GetValue(),
        )

    def Output(self, msg):
        print 's'
        self.message.SetLabel(msg)

    def CloseDFM(self):
        return self.socket.load_protocol_stack()


class TestThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.__parent = parent
        self.__stop = False

    def run(self):
        pass

    def trigger(self):
        if import_thread.isAlive():
            Utility.Alert.Info(u'正在导入数据,请稍后重试')
            return
        from scapy.layers.inet import Ether
        from scapy.sendrecv import sendp
        sendp(Ether(src=Utility.get_local_mac(), dst="00:00:01:02:03:04", type=0xf1f1))

    def close_dfm_test(self):
        self.wrapper(self.__parent.CloseDFM)

    def set_config_to_web(self):
        self.wrapper(self.__parent.SetConfig)

    def stop(self):
        self.__stop = True

    def wrapper(self, func, *args):
        if self.__stop:
            raise StandardError
        return func(*args)

    def is_web_server_started(self):
        try:
            session = requests.Session()
            resp = session.request(method='get', url='http://192.168.1.1/login.php', timeout=1)
            if resp.status_code == 200:
                return True
            return False
        except requests.ConnectTimeout:
            return False
        except requests.ReadTimeout:
            return False
        except requests.ConnectionError:
            time.sleep(1)
            return False
        finally:
            session.close()
