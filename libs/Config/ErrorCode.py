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
    SERIAL_EXCEPTION = ErrorCodeField(10003, "Serial communication error.")
    WRONG_TERMINATOR = ErrorCodeField(10004, "Can not find terminal symbol.")
    TIMING_ERROR = ErrorCodeField(10005, "Sequence Error Interrupt.")
