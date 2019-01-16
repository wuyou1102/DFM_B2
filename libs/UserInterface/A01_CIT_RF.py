# -*- encoding:UTF-8 -*-

import logging
import sys

import A01_CIT_Base

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(A01_CIT_Base.Frame):
    def __init__(self):
        A01_CIT_Base.Frame.__init__(self, title=u"射频测试", type="RF")
