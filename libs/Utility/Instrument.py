# -*- encoding:UTF-8 -*-
import pyvisa
import logging
import threading
import wx

logger = logging.getLogger(__name__)
FLAG = False


def Error(Message, From=None):
    title = u"错误" if From is None else u"来自 \"%s\" 的错误" % From
    logger.error(u'{title}:{Message}'.format(title=title, Message=Message))
    dialog = wx.MessageDialog(None, Message, title, wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Center()
    dialog.Destroy()

try:
    ResourceManager = pyvisa.ResourceManager()
    FLAG = True
except OSError:
    Error(u"如需自动测试，请先安装NI VISA。")
except ValueError:
    Error(u"如需自动测试，请先安装NI VISA。")


def list_resources():
    return ResourceManager.list_resources()

class SCPI(object):
    def __init__(self, port, timeout=3000):
        self.__port = port
        self.__timeout = timeout
        self.__session = self.__init_session()
        self.__lock = threading.Lock()
        self.model_name = self.__get_model_name()

    def __init_session(self):
        session = ResourceManager.open_resource(self.__port)
        session.timeout = self.__timeout
        return session

    def __get_model_name(self):
        model_info = self.execute_command('*IDN?')
        return model_info.split(',')[1].strip(' ')

    def disconnect(self):
        if self.__session:
            self.__session.close()

    def Set(self, command):
        if command.endswith('?'):
            raise IOError("Set command can not endswith \"?\"")
        output = self.execute_command(command=command)
        if output == pyvisa.constants.StatusCode.success:
            return True
        return False

    def Get(self, command):
        if not command.endswith('?'):
            raise IOError("Get command must endswith \"?\"")
        return self.execute_command(command=command)

    def __query(self, cmd):
        return self.__session.query(cmd).strip('\r\n')

    def __write(self, cmd):
        return self.__session.write(cmd)[1]

    def execute_command(self, command):
        logger.info('********************************************************')
        logger.info('* SCPI COMMAND:\"%s\"' % command)
        if self.__lock.acquire():
            try:
                result = self.__query(command) if command.endswith('?') else self.__write(command)
                logger.info("* STDOUT: {result}".format(result=repr(result)))
                return result
            finally:
                logger.info('********************************************************')
                self.__lock.release()


if __name__ == '__main__':
    resources = ResourceManager.list_resources()

    for resource in resources:
        inst = SCPI(resource)
        if inst.model_name == 'FSH8':
            print inst.model_name
            print inst.execute_command('CALC:MARK:FUNC:POW:SEL?')
        inst.disconnect()
