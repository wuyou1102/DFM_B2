# -*- encoding:UTF-8 -*-
from RF_TransmitBase import TransmitBase
from libs.Config import String


#         for p in ['2410', '2450', '2475', '5750', '5800', '5825']:
class Transmit2410(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2410, flag=String.RF_TRANSMIT_2410)


class Transmit2450(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2450, flag=String.RF_TRANSMIT_2450)


class Transmit2475(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=2475, flag=String.RF_TRANSMIT_2475)


class Transmit5750(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5750, flag=String.RF_TRANSMIT_5750)


class Transmit5800(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5800, flag=String.RF_TRANSMIT_5800)


class Transmit5850(TransmitBase):
    def __init__(self, parent, type):
        TransmitBase.__init__(self, parent=parent, type=type, freq=5850, flag=String.RF_TRANSMIT_5850)
