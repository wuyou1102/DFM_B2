# -*- encoding:UTF-8 -*-
from RF_TransmitBase import TransmitBase
from libs.Config import String


class Transmit2400A(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2450, RoadA=True)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_2400A

    @staticmethod
    def GetName():
        return u" 发射功率 [2400A] "


class Transmit2400B(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2450, RoadA=False)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_2400B

    @staticmethod
    def GetName():
        return u" 发射功率 [2400B] "


class Transmit5800A(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5800, RoadA=True)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_5800A

    @staticmethod
    def GetName():
        return u" 发射功率 [5800A] "


class Transmit5800B(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5800, RoadA=False)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_TRANSMIT_5800B

    @staticmethod
    def GetName():
        return u" 发射功率 [5800B] "
