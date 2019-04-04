# -*- encoding:UTF-8 -*-

import logging
import sys
import A03_FactoryInspection_Base

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(A03_FactoryInspection_Base.Frame):
    def __init__(self):
        A03_FactoryInspection_Base.Frame.__init__(self, title=u"出厂检查（全向天线）", type_="Omni")
