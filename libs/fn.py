# -*- coding: utf-8 -*-
import random
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


def get_lonlat(lon, lat):
    lon += 0.001 * random.randint(-5, 5)
    lat += 0.001 * random.randint(0, 5)

    if lon > 180 or lon < -180 or lat > 90 or lat < -90:
        lon = 104.03974
        lat = 30.66578

    return int(lon * 100000), int(lat * 100000)

