# -*- encoding:UTF-8 -*-
import subprocess
import logging
from libs import Command
import time
from psutil import net_if_addrs
import os

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


def convert_freq_point(value):
    def swap_to_d1d3(d3t1):
        d3t1 = [d3t1[i:i + 2] for i in xrange(0, len(d3t1), 2)]
        return ''.join(d3t1[::-1])

    value = '{0:08x}'.format(int(value, 16))
    d3d1 = value[0:6]
    d0 = value[6:].upper()
    rf_multi = 30 if d0 in ['4B', '4C', '4D', '4E', '4F', '50', '51', '52', '53'] else 60
    d1d3 = swap_to_d1d3(d3d1)
    d1d3 = int(d1d3, 16)
    d0 = int(d0, 16)
    f = round((d1d3 / 16777216.0 + d0) * rf_multi, 2)
    return str(f)


def get_local_mac():
    for k, v in net_if_addrs().items():
        interface_name = k.decode("gbk")
        print interface_name
        if interface_name in [u"本地连接", u"以太网"]:
            print v[0].address.replace("-", ":")
            return v[0].address.replace("-", ":")
        elif u"本地连接" in interface_name:
            print v[0].address.replace("-", ":")
            return v[0].address.replace("-", ":")
    raise IOError


def is_device_started(address='192.168.1.1', timeout=10):
    result = os.popen("ping {address} -w {timeout} -n 1".format(address=address, timeout=timeout)).read()
    if "TTL=64" in result:
        return True
    return False


if __name__ == '__main__':
    while True:
        print is_device_started()
