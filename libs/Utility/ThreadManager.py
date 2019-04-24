# -*- encoding:UTF-8 -*-
import threading
import logging
from libs.Config.ErrorCode import ErrorCode
import types
from random import choice

__log = logging.getLogger(__name__)

__thread_pool = dict()


def query_thread():
    __log.debug(msg="%-10s|%50s" % ("STATE", "NAME"))
    for k, v in __thread_pool.items():
        if v.isAlive():
            __log.debug(msg="%-10s|%50s" % ("RUNNING", k))
        else:
            __log.debug(msg="%-10s|%50s" % ("DONE", k))
            del __thread_pool[k]


def append_thread(target, allow_dupl=False, **kwargs):
    try:
        if not isinstance(target, types.FunctionType) and not isinstance(target, types.MethodType):
            __log.error(ErrorCode.TARGET_NOT_FUNCTION.MSG)
            return False
        if allow_dupl:
            return __append_thread_duplicate(target=target, **kwargs)
        else:
            return __append_thread(target=target, **kwargs)
    finally:
        query_thread()


def is_alive(name):
    _thread = __thread_pool.get(name)
    if _thread and _thread.isAlive():
        return True
    return False


def __append_thread_duplicate(target, **kwargs):
    def add_suffix(name):
        name += ':'
        for x in range(20):
            name += choice('0123456789ABCDEF')
        return name

    name = kwargs.get('thread_name', target.__name__)
    name = add_suffix(name)
    kwargs['thread_name'] = name
    return __start_thread(target=target, **kwargs)


def __append_thread(target, **kwargs):
    thread_name = kwargs.get('thread_name', target.__name__)
    kwargs['thread_name'] = thread_name
    _thread = __thread_pool.get(thread_name)
    if _thread and _thread.isAlive():
        __log.warn('{code}:{msg}:{name}'.format(code=ErrorCode.TARGET_ALREADY_EXIST, name=target.__name__,
                                                msg=ErrorCode.TARGET_ALREADY_EXIST.MSG))
        return False
    return __start_thread(target=target, **kwargs)


def __start_thread(target, thread_name, **kwargs):
    t = threading.Thread(target=target, kwargs=kwargs)
    t.setDaemon(True)
    __thread_pool[thread_name] = t
    t.start()
    # __log.debug(msg="%-10s|%50s" % ("STARTED", thread_name))
    return t


if __name__ == '__main__':
    pass
