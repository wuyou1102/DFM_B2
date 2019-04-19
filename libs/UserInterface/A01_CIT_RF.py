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
        if Instrument.FLAG:
            print Instrument.list_resources()
            resources = Instrument.list_resources()
            for resource in resources:
                if resource in [u'ASRL1::INSTR', u'ASRL10::INSTR']:
                    continue
                inst = Instrument.SCPI(resource)
                if inst.model_name in ["N9020A"]:  # 信号分析仪
                    self.__Analyzer = SignalAnalyzer(instrument=inst)
                elif inst.model_name in ["N5172B"]:  # 信号发生器
                    self.__Sources = SignalSources(instrument=inst)
                else:
                    logger.error("Unknown Instrument [%s]" % inst.model_name)
            Utility.append_thread(self.__init_instrument)

    def __init_instrument(self):
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
        result = result and self.MOD(ON=True)
        result = result and self.RF(ON=True)
        result = result and self.SetFileData(config.get("wave_file", "SR_SLOT_20M_16QAM_12_1P25X4_1T.DAT"))
        result = result and self.ARB(ON=True)
        result = result and self.ALC(ON=False)
        result = result and self.SetARBClock(mHz=22.4)
        result = result and self.SetFrequency(mHz=2400)
        if result:
            Utility.Alert.Info(u"信号发生器初始化成功。")
        else:
            Utility.Alert.Error(u"信号发生器初始化失败，请重试")
        return result

    def Reset(self):
        command = '*RST'
        return self.__inst.Set(command)

    def SetFrequency(self, mHz=2400):
        command = ":FREQ:FIXed {value}MHz".format(value=mHz)
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


class SignalAnalyzer(object):
    def __init__(self, instrument):
        self.__inst = instrument

    def init_analyzer_setting(self):
        config = Utility.ParseConfig.get(Path.CONFIG, "SignalAnalyzer")
        result = True
        result = result and self.EnterBurstPower()
        result = result and self.SetPowerAtt(0)
        result = result and self.SetBrustRracRlev(config.get("ref_level", 40))
        result = result and self.SetCorrOffs(config.get("gain", 60.0))
        result = result and self.SetMeasAsThreshold()
        result = result and self.SetMeasThrLevel(config.get("thr_level", 15))
        result = result and self.SetTriggerMode(mode="IMM")
        result = result and self.SetSweepTime(ms=50)
        result = result and self.SetAvg(ON=False)
        # result = result and self.SetIFLevel()
        result = result and self.SetBandWidth(20)
        if result:
            Utility.Alert.Info(u"频谱仪初始化成功。")
        else:
            Utility.Alert.Error(u"频谱仪初始化失败，请重试")
        return result

    def SetAvg(self, ON=True):
        STAT = "ON" if ON else "OFF"
        command = ":TXPower:AVERage %s" % STAT
        return self.__inst.Set(command)

    def SetIFLevel(self, level=10):
        command = ":TRIGger:IF:LEVel {value}".format(value=level)
        return self.__inst.Set(command)

    def SetSweepTime(self, ms=1000):
        command = "TXP:SWE:TIME %s ms" % ms
        return self.__inst.Set(command)

    def EnterBurstPower(self):
        command = "CONF:BPOW"
        return self.__inst.Set(command)

    def SetBrustRracRlev(self, dBm=40):
        command = "DISP:TXP:VIEW:WIND:TRAC:Y:RLEV {value}dBm".format(value=dBm)
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

    def SetMeasThrLevel(self, dBm=10):
        command = "TXP:THR -{value}".format(value=dBm)
        return self.__inst.Set(command)

    def SetTriggerMode(self, mode='VIDeo'):
        command = "TRIG:TXP:SOUR {mode}".format(mode=mode)
        return self.__inst.Set(command)

    def SetBandWidth(self, mHz=20):
        command = "TXP:BAND {value}kHz".format(value=mHz * 1000)
        return self.__inst.Set(command)

    def GetBurstPower(self):
        command = "FETC:BPOW?"
        return self.__inst.Get(command)

    def SetPowerAtt(self, dBm):
        command = "POW:ATT {value}".format(value=dBm)
        return self.__inst.Set(command)


if __name__ == '__main__':
    x = Instrument.list_resources()[0]
    init = Instrument.SCPI(x)
    # a = SignalAnalyzer(instrument=init)
    #
    # a()
    init.execute_command("BPOWer:AVER 0")
    init.execute_command("BPOWer:AVER?")
    init.execute_command("BPOWer:AVER:COUNt 1")
    init.execute_command("BPOWer:AVER:COUNt?")
    # for x in range(2410, 2666):
    #     print time.time()
    #     a.SetFrequency(x)
    #     print time.time()
    # a.SetPower()
    init.disconnect()
