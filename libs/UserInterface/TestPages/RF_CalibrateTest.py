# -*- encoding:UTF-8 -*-
from RF_CalibrateBase import CalibrateBase
from libs.Config import String


#         for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
class Calibrate5800(CalibrateBase):
    def __init__(self, parent, type):
        CalibrateBase.__init__(self, parent=parent, type=type, freq=5800)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_CALIBRATE_5800

    @staticmethod
    def GetName():
        return u" 校准测试 [5800-A] "

    def get_gain_unit(self):
        return 0.5

    def get_gain_gap(self):
        return -6, 6


class Calibrate2450(CalibrateBase):
    def __init__(self, parent, type):
        CalibrateBase.__init__(self, parent=parent, type=type, freq=2450)

    @staticmethod
    def GetFlag(t):
        if t == "RF":
            return String.RF_CALIBRATE_2400

    @staticmethod
    def GetName():
        return u" 校准测试 [2450-A] "

    def get_gain_unit(self):
        return 1.0

    def get_gain_gap(self):
        return -3, 3
