# -*- coding: utf-8 -*-
import re

from tornado.options import options


def get_seq(sn):
    options.thread_lock.acquire()
    try:
        options.tracker[sn]['seq'] += 1
        if options.tracker[sn]['seq'] > 255:
            options.tracker[sn]['seq'] = 1
    finally:
        options.thread_lock.release()
    return options.tracker[sn]['seq']


def fmt_iccid(iccid):
    iccid_lst = re.findall(r'(.{2})', iccid)
    return [int(item, 16) for item in iccid_lst]

