# -*- encoding:UTF-8 -*-
# from libs.UserInterface.TestPages.EthernetTest import Ethernet
# from libs.UserInterface.TestPages.USBTest import USB
# from libs.UserInterface.TestPages.RF_TransmitTest import Transmit2410, Transmit2450, Transmit2475, Transmit5750, Transmit5800, Transmit5850
from libs.UserInterface.TestPages.SwitchTest import Switch
from libs.UserInterface.TestPages.LampHolderTest import LampHolder
from libs.UserInterface.TestPages.WatchDogTest import WatchDog
from libs.UserInterface.TestPages.LEDTest import LED
from libs.UserInterface.TestPages.FPVTest import FPV
from libs.UserInterface.TestPages.RF_ReceiveTest import \
    Receive2410, Receive2450, Receive2475, \
    Receive5750, Receive5800, Receive5850
from libs.UserInterface.TestPages.RF_CalibrateTest import Calibrate2450, Calibrate5800
from libs.UserInterface.TestPages.RF_TransmitTest import Transmit2450A, Transmit2450B, Transmit5800A, Transmit5800B

PCBA_CASES = [LampHolder, Switch, WatchDog]
MACHINE_CASES = [LED, Switch, FPV, WatchDog]
RF_CASES = [
    Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5850,
    Calibrate2450, Transmit2450A, Transmit2450B, Calibrate5800, Transmit5800A, Transmit5800B
]
RF_CASES_2400 = [
    Receive5750, Receive5800, Receive5850, Calibrate5800, Transmit5800A, Transmit5800B
]
RF_CASE_5800 = [
    Receive2410, Receive2450, Receive2475, Calibrate2450, Transmit2450A, Transmit2450B,
]
