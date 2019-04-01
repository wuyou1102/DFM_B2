# -*- encoding:UTF-8 -*-

import logging
import sys
from libs import Utility
from libs.Config import Path
from libs.Utility import Instrument
import A01_CIT_Base

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(A01_CIT_Base.Frame):
    def __init__(self):
        self.__Sources = None
        self.__Analyzer = None
        A01_CIT_Base.Frame.__init__(self, title=u"射频测试", type="RF", size=(1100, 700))
        Utility.append_thread(self.__init_instrument)

    def __init_instrument(self):
        resources = Instrument.list_resources()
        for resource in resources:
            if resource in [u'ASRL1::INSTR']:
                continue
            inst = Instrument.SCPI(resource)
            if inst.model_name in ["N9020A"]:  # 信号分析仪
                self.__Analyzer = SignalAnalyzer(instrument=inst)
            elif inst.model_name in ["N5172B"]:  # 信号发生器
                self.__Sources = SignalSources(instrument=inst)
            else:
                logger.error("Unknown Instrument [%s]" % inst.model_name)
        if self.__Sources:
            Utility.append_thread(self.__Sources.init_sources_setting)
        if self.__Analyzer:
            Utility.append_thread(self.__Analyzer.init_analyzer_setting)
        if self.__Sources is None:
            Utility.Alert.Error(u"没有找到已连接的信号发生器，接收灵敏度测试无法自动测试")
        if self.__Analyzer is None:
            Utility.Alert.Error(u"没有找到已连接的信号分析仪，发送功率测试无法自动测试")

    @property
    def SignalSources(self):
        return self.__Sources

    @property
    def SignalAnalyzer(self):
        return self.__Analyzer


class SignalSources(object):
    def __init__(self, instrument):
        self.__inst = instrument

    def init_sources_setting(self):
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalSources")
        result = True
        result = result and self.Reset()
        result = result and self.SetPower(config.get("Power", 50.0))
        result = result and self.MOD(ON=True)
        result = result and self.RF(ON=True)
        result = result and self.SetFileData(config.get("File", "SR_SLOT_20M_16QAM_12_1P25X4_1T.DAT"))
        result = result and self.ARB(ON=True)
        result = result and self.ALC(ON=False)
        result = result and self.SetARBClock(mHz=20)
        return result

    def Reset(self):
        command = '*RST'
        return self.__inst.Set(command)

    def SetFrequency(self, MHz=2400):
        command = ":FREQ:FIXed {value}MHz".format(value=MHz)
        return self.__inst.Set(command)

    def SetPower(self, DBM=10.1):
        command = ":POWer:LEVel -{value}DBM".format(value=DBM)
        return self.__inst.Set(command)

    def SetFileData(self, file_name='SR_SLOT_20M_16QAM_12_1P25X4_1T.DAT'):
        command = ':SOURce:RADio:ARB:WAVeform "WFM1:{file_name}"'.format(file_name=file_name)
        return self.__inst.Set(command)

    def SetARBClock(self, mHz=20):
        command = 'RADio:ARB:SCLock:RATE {value}kHz'.format(value=mHz * 1000)
        return self.__inst.Set(command)

    def ARB(self, ON=True):
        command = ":RAD:ARB ON" if ON else ":RAD:ARB OFF"
        return self.__inst.Set(command)

    def ALC(self, ON=True):
        command = ":POWer:ALC ON" if ON else ":POWer:ALC OFF"
        return self.__inst.Set(command)

    def MOD(self, ON=True):
        command = "OUTP:MOD ON" if ON else "OUTP:MOD OFF"
        return self.__inst.Set(command)

    def RF(self, ON=True):
        command = "OUTP ON" if ON else "OUTP OFF"
        return self.__inst.Set(command)


# x信号发生器
# for x in range(2410,2450):
#     inst.send_command(command="FREQ %s MHz" % x)
#     time.sleep(1)
# inst.send_command(command=":POWer:LEVel -32.1DBM")
# inst.send_command(command=":FREQuency:FIXed 2.51GHZ")
# inst.send_command('RADio:ARB:SCLock:RATE 22900kHz')
#       inst.send_command('RADio:ARB:SCLock:RATE?')
# inst.send_command(":RAD:ARB ON")
# inst.send_command(":RAD:ARB?")
# inst.send_command(":POWer:ALC OFF")
# inst.send_command(":POWer:ALC?")
# SR_SLOT_20M_16QAM_12_1P25X4_1T
# inst.send_command(':SOURce:RADio:ARB:WAVeform "WFM1:SR_SLOT_20M_16QAM_12_1P25X4_1T.DAT"')


# print '======================================================================================='
# inst.send_command("CONF:BPOW")
#
# inst.send_command("DISP:TXP:VIEW:WIND:TRAC:Y:RLEV 40dBm")
# inst.send_command("CORR:SA:GAIN -20.2")
# inst.send_command("FREQ:CENT 2410MHz")
# inst.send_command("TXP:METH THR")
# inst.send_command("TXP:THR -15")
# inst.send_command("TRIG:TXP:SOUR IMM")
# inst.send_command("TXP:BAND 20000kHz")
# for x in range(10):
#     time.sleep(1)
#     print inst.execute_command("FETC:BPOW?")


class SignalAnalyzer(object):
    def __init__(self, instrument):
        self.__inst = instrument

    def init_analyzer_setting(self):
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer")
        result = True
        result = result and self.EnterBurstPower()
        result = result and self.SetBrustRracRlev(config.get("RLEV", 40))
        result = result and self.SetCorrOffs(config.get("GAIN", 20.0))
        result = result and self.SetMeasAsThreshold()
        result = result and self.SetMeasThrLevel(config.get("THR_LEVEL", 15))
        result = result and self.SetTriggerImmediately()
        result = result and self.SetBandWidth(20)
        return result

    def EnterBurstPower(self):
        command = "CONF:BPO"
        return self.__inst.Set(command)

    def SetBrustRracRlev(self, dBm=40):
        command = "DISP:TXP:VIEW:WIND:TRAC:Y:RLEV {value}dBm", format(value=dBm)
        return self.__inst.Set(command)

    # 设置外部补偿电平
    def SetCorrOffs(self, dBm=20.1):
        command = "CORR:SA:GAIN -{value}".format(value=dBm)
        return self.__inst.Set(command)

    def SetFrequency(self, MHz=2400):
        command = "FREQ:CENT {value}MHz".format(value=MHz)
        return self.__inst.Set(command)

    def SetMeasAsThreshold(self):
        command = "TXP:METH THR"
        return self.__inst.Set(command)

    def SetMeasThrLevel(self, dBm=15):
        command = "TXP:THR -{value}".format(value=dBm)
        return self.__inst.Set(command)

    def SetTriggerImmediately(self):
        command = "TRIG:TXP:SOUR IMM"
        return self.__inst.Set(command)

    def SetBandWidth(self, mHz=20):
        command = "TXP:BAND {value}kHz".format(value=mHz * 1000)
        return self.__inst.Set(command)

    def GetBurstPower(self):
        command = "FETC:BPOW?"
        return self.__inst.Get(command)


if __name__ == '__main__':
    x = Instrument.list_resources()[0]
    init = Instrument.SCPI(x)
    a = SignalSources(instrument=init)
    a.SetFileData()
    import time

    print time.time()
    a.init_sources_setting()
    print time.time()
    # for x in range(2410, 2666):
    #     print time.time()
    #     a.SetFrequency(x)
    #     print time.time()
    # a.SetPower()
    init.disconnect()
