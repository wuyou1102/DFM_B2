# -*- encoding:UTF-8 -*-
import six


class ErrorCodeField(int):
    def __new__(cls, error_code, message=u""):
        obj = int.__new__(cls, error_code)
        obj.MSG = message
        return obj


class ErrorCodeMetaClass(type):
    def __new__(cls, name, bases, namespace):
        code_message_map = {}
        for k, v in namespace.items():
            if getattr(v, '__class__', None) and isinstance(v, ErrorCodeField):
                if code_message_map.get(v):
                    raise ValueError("duplicated codde {0} {1}".format(k, v))
                code_message_map[v] = getattr(v, 'MSG', "")
        namespace["CODE_MESSAGE_MAP"] = code_message_map
        return type.__new__(cls, name, bases, namespace)


class BaseErrorCode(six.with_metaclass(ErrorCodeMetaClass)):
    CODE_MESSAGE_MAP = NotImplemented


class ErrorCode(BaseErrorCode):
    TARGET_ALREADY_EXIST = ErrorCodeField(10001, "Same target is already running.")
    TARGET_NOT_FUNCTION = ErrorCodeField(10002, "The target cannot be called.It's not a function.")
    SERIAL_EXCEPTION = ErrorCodeField(10003, u"串口通信异常，请检查串口是否正常，然后重试。")
    WRONG_TERMINATOR = ErrorCodeField(10004, u"错误的结束符，请重试。")
    EMPTY_OUTPUT_EXCEPTION = ErrorCodeField(10005, u"空白输出，请重试。")
    TIMING_ERROR = ErrorCodeField(10006, "Sequence Error Interrupt.")
    SOCKET_EXCEPTION = ErrorCodeField(10007, u"通信异常，请检查网络后重试。")
