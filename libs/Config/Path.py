import os
import sys

__ABS = os.path.abspath(os.path.dirname(sys.argv[0]))


def join(*args):
    p = os.path.join(*args)
    if not os.path.exists(p):
        os.makedirs(p)
    return p


LOG_SAVE = join(__ABS, "Log")
CONFIG = os.path.join(__ABS, "B2.conf")
