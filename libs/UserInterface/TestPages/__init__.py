from EthernetTest import EthernetTest
from SwitchTest import SwitchTest
from USBTest import USBTest
from LightTest import LightTest
from FPVTest import FPVTest
from RF_Receive import ReceiveTest
from RF_Transmit import TransmitTest
from Base import Variable

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest]
MACHINE_CASES = [FPVTest]
RF_CASES = [ReceiveTest, TransmitTest]
