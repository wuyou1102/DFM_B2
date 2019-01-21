from EthernetTest import EthernetTest
from SwitchTest import SwitchTest
from USBTest import USBTest
from LightTest import LightTest
from FPVTest import FPVTest
from RF_ReceiveTest import Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5825
from RF_TransmitBase import TransmitTest
from Base import Variable

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest]
MACHINE_CASES = [FPVTest]
RF_CASES = [Receive2410, Receive2450, Receive2475, Receive5750, Receive5800, Receive5825, TransmitTest]
