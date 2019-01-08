from EthernetTest import EthernetTest
from SwitchTest import SwitchTest
from USBTest import USBTest
from LightTest import LightTest
from FPVTest import FPVTest
from Base import Variable

PCBA_CASES = [EthernetTest, SwitchTest, LightTest, USBTest,FPVTest]

# MACHINE_CASES = [EthernetTest]

MACHINE_CASES = [EthernetTest, SwitchTest, LightTest, USBTest,FPVTest]
