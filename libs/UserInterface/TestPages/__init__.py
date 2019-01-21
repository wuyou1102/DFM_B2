from EthernetTest import EthernetTest
from SwitchTest import SwitchTest
from USBTest import USBTest
from LightTest import LightTest
from FPVTest import FPVTest
from RF_ReceiveBase import ReceiveBase
from RF_TransmitBase import TransmitTest
from Base import Variable

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest]
MACHINE_CASES = [FPVTest]
RF_CASES = [ReceiveBase, TransmitTest]
