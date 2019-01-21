from EthernetTest import EthernetTest
from SwitchTest import SwitchTest
from USBTest import USBTest
from LightTest import LightTest
from FPVTest import FPVTest
from RF_ReceiveTest import Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5850
from RF_TransmitTest import Transmit2410, Transmit2450, Transmit2475, Transmit5750, Transmit5800, Transmit5850
from Base import Variable

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest]
MACHINE_CASES = [FPVTest]
RF_CASES = [
    Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5850,
    Transmit2410, Transmit2450, Transmit2475, Transmit5750, Transmit5800, Transmit5850
]
