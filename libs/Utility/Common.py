# -*- encoding:UTF-8 -*-
import subprocess
import logging
from libs import Command
import time

__logger = logging.getLogger(__name__)


class ExecuteResult(object):
    def __init__(self, exit_code, outputs):
        self._exit_code = exit_code
        self._outputs = outputs

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def outputs(self):
        return self._outputs


def param_to_property(*props, **kwprops):
    if props and kwprops:
        raise SyntaxError("Can not set both props and kwprops at the same time.")

    class Wrapper(object):
        def __init__(self, func):
            self.func = func
            self.kwargs, self.args = {}, []

        def __getattr__(self, attr):
            if kwprops:
                for prop_name, prop_values in kwprops.items():
                    if attr in prop_values and prop_name not in self.kwargs:
                        self.kwargs[prop_name] = attr
                        return self
            elif attr in props:
                self.args.append(attr)
                return self
            raise AttributeError("%s parameter is duplicated or not allowed!" % attr)

        def __call__(self, *args, **kwargs):
            if kwprops:
                kwargs.update(self.kwargs)
                self.kwargs = {}
                return self.func(*args, **kwargs)
            else:
                new_args, self.args = self.args + list(args), []
                return self.func(*new_args, **kwargs)

    return Wrapper


def execute_command(command, encoding=None):
    outputs = list()
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
    __logger.debug('********************************************************')
    __logger.debug('* EXECUTED COMMAND:\"%s\"' % command)
    try:
        for line in iter(p.stdout.readline, b''):
            if encoding is None:
                line = line.strip('\r\n')
            else:
                line = line.decode(encoding=encoding, errors="strict").strip('\r\n')
            __logger.debug("* STDOUT: {line}".format(line=line))
            outputs.append(line)
    finally:
        exit_code = p.wait()
        p.kill()
        __logger.debug('* EXIT CODE: \"%s\"' % exit_code)
        __logger.debug('********************************************************')
        return ExecuteResult(exit_code=exit_code, outputs=outputs)


def get_adb_devices():
    devices = list()
    result = execute_command(Command.adb.devices())
    for line in result.outputs:
        if 'device' in line and 'List of' not in line:
            devices.append(line[:line.index('\t')])
    return devices


def get_visa_resources():
    import pyvisa
    resource_manager = pyvisa.ResourceManager()
    return resource_manager.list_resources()


def get_serial_ports():
    import serial.tools.list_ports
    ports = list()
    port_list = serial.tools.list_ports.comports()
    if len(port_list) == 0:
        __logger.info(u'Can not find ports.')
        return ports
    else:
        for port in list(port_list):
            port_name = port[1]
            ports.append(port_name)
        return sorted(ports, reverse=True)


def get_timestamp(time_fmt='%Y_%m_%d-%H_%M_%S', t=None):
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


def get_time(time_fmt='%H:%M:%S', t=None):
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


def generator():
    count = 0
    while True:
        count += 1
        yield count


if __name__ == '__main__':
    res = execute_command(Command.adb.shell_command('ps |grep \"ddd\"'))
    print res.outputs
    print res.exit_code
