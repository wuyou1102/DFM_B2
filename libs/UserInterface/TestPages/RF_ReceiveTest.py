# -*- encoding:UTF-8 -*-
from RF_ReceiveBase import ReceiveBase
from libs.Config import String


#         for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
class Receive2410(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=2410)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_2410

    @staticmethod
    def GetName():
        return u"接收灵敏度 [2410]"


class Receive2450(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=2450)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_2450

    @staticmethod
    def GetName():
        return u"接收灵敏度 [2450]"


class Receive2475(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=2475)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_2475

    @staticmethod
    def GetName():
        return u"接收灵敏度 [2475]"


class Receive5750(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=5750)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_5750

    @staticmethod
    def GetName():
        return u"接收灵敏度 [5750]"


class Receive5800(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=5800)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_5800

    @staticmethod
    def GetName():
        return u"接收灵敏度 [5800]"


class Receive5850(ReceiveBase):
    def __init__(self, parent, type):
        ReceiveBase.__init__(self, parent=parent, type=type, freq=5850)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_RECEIVE_5850

    @staticmethod
    def GetName():
        return u"接收灵敏度 [5850]"
