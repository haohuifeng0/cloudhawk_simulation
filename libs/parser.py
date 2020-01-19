# -*- coding: utf-8 -*-
import struct

from libs.CH import length, fmt
from libs.dotdict import DotDict


class BaseParser(object):

    def __init__(self, packet):
        self.header, self.body = self.parse_head(packet)

    def parse_head(self, packet):
        keys = ['cmd_type', 'cmd_num', 'success', 'seq', 'timestamp', ]
        header = DotDict()
        start_idx = 0
        for key in keys:
            length_ = length[key]
            end_idx = start_idx + length_
            value = packet[start_idx:end_idx]
            value_str = ""
            value_lst = struct.unpack('!' + fmt[key], value)
            for item in value_lst:
                if isinstance(item, bytes):
                    item = str(item, encoding='utf-8')
                value_str += str(item)
            header[key] = value_str
            start_idx += length_
        body = packet[start_idx:]

        return header, body


class LoginParser(object):

    def __init__(self, header, body):
        body = self.parse(body)
        header.update(body)
        self.data = header

    def parse(self, body):
        keys = ['sessionID', 'login_status', ]
        data = dict()
        start_idx = 0
        for key in keys:
            length_ = length[key]
            end_idx = start_idx + length_
            value = body[start_idx:end_idx]
            value_str = ""
            value_lst = struct.unpack('!' + fmt[key], value)
            for item in value_lst:
                value_str += str(item)
            data[key] = value_str
            start_idx += length_

        return data


class ConfigParser(object):

    def __init__(self, header, body):
        body = self.parse(body)
        header.update(body)
        self.data = header

    def parse(self, body):
        keys = ['body_length', 'config_args_num', 'alert_flags', 'config_args_length']
        data = dict()
        start_idx = 0
        for key in keys:
            length_ = length[key]
            end_idx = start_idx + length_
            value = body[start_idx:end_idx]
            if not value:
                break
            value_str = ""
            value_lst = struct.unpack('!' + fmt[key], value)
            for item in value_lst:
                value_str += str(item)
            data[key] = value_str
            start_idx += length_

        data['args'] = body[start_idx:]
        return data


class Parser():
    def parse_login(self, dat):
        bp = BaseParser(dat)
        header = bp.header
        body = bp.body
        return LoginParser(header, body)

    def parse_base(self, bp):
        return BaseParser(bp)

    def parse_config(self, dat):
        bp = BaseParser(dat)
        header = bp.header
        body = bp.body
        return ConfigParser(header, body)
