# -*- encoding:UTF-8 -*-
import os
import sys


def is_debug():
    import uuid
    import platform
    if platform.system() != "Windows":
        return False
    return uuid.UUID(int=uuid.getnode()).get_hex() != '000000000000000000008cec4b410724'


abs_path = os.path.abspath(os.path.dirname(sys.argv[0]))
__fastboot = os.path.join(abs_path, 'resource', 'binary', 'android_sdk', 'fastboot.exe') if is_debug() else "fastboot"


def reboot(serial=''):
    if serial:
        return '{fastboot} -s {serial} reboot'.format(fastboot=__fastboot, serial=serial)
    return '{fastboot} reboot'.format(fastboot=__fastboot)


def devices():
    return '{fastboot} devices'.format(fastboot=__fastboot)


def wait_for_device(serial=''):
    if serial:
        return '{fastboot} -s {serial} wait-for-device'.format(fastboot=__fastboot, serial=serial)
    return '{fastboot} wait-for-device'.format(fastboot=__fastboot)


def erase(partition, serial=''):
    if serial:
        return '{fastboot} -s {serial} erase {partition}'.format(fastboot=__fastboot, serial=serial,
                                                                 partition=partition)
    return '{fastboot} erase {partition}'.format(fastboot=__fastboot, partition=partition)


def flash(partition, image, serial=''):
    if serial:
        return '{fastboot} -s {serial} flash {partition} {image}'.format(fastboot=__fastboot, serial=serial,
                                                                         partition=partition, image=image)
    return '{fastboot} flash {partition} {image}'.format(fastboot=__fastboot, partition=partition, image=image)
