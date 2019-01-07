# -*- coding:utf-8 -*-
from ConfigParser import ConfigParser
import os


def read(path):
    data = dict()
    parser = ConfigParser()
    parser.read(path)
    for section in parser.sections():
        dict_section = dict()
        for option in parser.options(section):
            dict_section[option] = parser.get(section=section, option=option)
        data[section] = dict_section
    return data


def get(path, section, option=None):
    parser = ConfigParser()
    parser.read(path)
    if not parser.has_section(section=section):
        return dict()
    if option is None:
        dict_section = dict()
        for option in parser.options(section):
            dict_section[option] = parser.get(section=section, option=option)
        return dict_section
    else:
        return parser.get(section=section, option=option)


def write(path, data):
    parser = ConfigParser()
    for section in data.keys():
        parser.add_section(section)
        for option, value in data[section].items():
            parser.set(section=section, option=option, value=value)
    __save(parser=parser, path=path)


def modify(path, data):
    parser = ConfigParser()
    parser.read(path)
    for section in data.keys():
        if not parser.has_section(section):
            parser.add_section(section)
        for option, value in data[section].items():
            parser.set(section=section, option=option, value=value)
    __save(parser=parser, path=path)


def delete(path, section, option=None):
    parser = ConfigParser()
    parser.read(path)
    if option is None:
        parser.remove_section(section=section)
    else:
        parser.remove_option(section=section, option=option)
    __save(parser=parser, path=path)


def __save(parser, path):
    # mode = "w+" if os.path.exists(path=path) else "w"
    with open(path, "w+") as config:
        parser.write(config)


if __name__ == '__main__':
    # data = {
    #     "aaaaaaaaa":
    #         {
    #             "bbb": "5123213213213",
    #             "ccc": "dddd"
    #         }
    # }
    print get("z.conf", section="ddd", option="ccc")
