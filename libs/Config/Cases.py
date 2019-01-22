# -*- encoding:UTF-8 -*-
from libs.UserInterface.TestPages.EthernetTest import EthernetTest
from libs.UserInterface.TestPages.EthernetTest import EthernetTest
from libs.UserInterface.TestPages.SwitchTest import SwitchTest
from libs.UserInterface.TestPages.USBTest import USBTest
from libs.UserInterface.TestPages.LightTest import LightTest
from libs.UserInterface.TestPages.FPVTest import FPVTest
from libs.UserInterface.TestPages.RF_ReceiveTest import \
    Receive2410, Receive2450, Receive2475, \
    Receive5750, Receive5800, Receive5850
from libs.UserInterface.TestPages.RF_TransmitTest import \
    Transmit2410, Transmit2450, Transmit2475, \
    Transmit5750, Transmit5800, Transmit5850

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest]
MACHINE_CASES = [FPVTest]
RF_CASES = [
    Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5850,
    Transmit2410, Transmit2450, Transmit2475, Transmit5750, Transmit5800, Transmit5850,
]
