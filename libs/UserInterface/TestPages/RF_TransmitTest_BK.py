# -*- encoding:UTF-8 -*-
from RF_TransmitBase_BK import TransmitBase
from libs.Config import String


#         for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
class Transmit2410(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2410)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_2410

    @staticmethod
    def GetName():
        return u" 发射功率 [2410] "


class Transmit2450(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2450)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_2450

    @staticmethod
    def GetName():
        return u" 发射功率 [2450] "


class Transmit2475(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2475)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_2475

    @staticmethod
    def GetName():
        return u" 发射功率 [2475] "


class Transmit5750(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5750)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_5750

    @staticmethod
    def GetName():
        return u" 发射功率 [5750] "


class Transmit5800(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5800)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_5800

    @staticmethod
    def GetName():
        return u" 发射功率 [5800] "


class Transmit5850(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5850)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_5850

    @staticmethod
    def GetName():
        return u" 发射功率 [5850] "
