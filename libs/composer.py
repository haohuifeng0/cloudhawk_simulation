# -*- coding: utf-8 -*-
import binascii
import struct
import random

import logging
import time

from libs import fn

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S')


class Composer(object):
    # 3.3

    def __init__(self, lon=104.03974, lat=30.66578):
        self.logging = logging
        self.lon = lon
        self.lat = lat

    def get_lonlat(self):
        self.lon += 0.001 * random.randint(-5, 5)
        self.lat += 0.001 * random.randint(0, 5)

        if self.lon > 180 or self.lon < -180 or self.lat > 90 or self.lat < -90:
            self.lon = 104.03974
            self.lat = 30.66578

        return self.lon * 100000, self.lat * 100000

    def compose_login(self, seq, sn, iccid):
        # U1
        # 'iccid', 'reason', 'sn', 'Firmware Version'
        fmt = '!sBBBQ10BB5B4B'
        value = [b'U', 1, 48, seq, 0, ] + iccid
        value += [0, ] + sn + [66, 4, 6, 123]
        self.logging.info("login_mg: %s", value)
        login_mg = struct.pack(fmt, *value)
        return login_mg

    def compose_heartbat(self, seq, iccid, args):
        fmt = '!sBBBQ10BBBBBBB'
        value = [b'U', 2, 48, seq, args.sessionID
                 ] + iccid + [args.bat, args.chg, args.gsm, args.temp, 0, 0]
        self.logging.info("realtime_mg: %s", value)
        heartbeat_mg = struct.pack(fmt, *value)
        return heartbeat_mg

    def compose_config(self, seq, iccid, sessionID):
        fmt = '!sBBBQ10B'
        value = [b'U', 3, 48, seq, sessionID] + iccid
        self.logging.info("config_mg: %s", value)
        config_mg = struct.pack(fmt, *value)
        return config_mg

    def compose_u4(self, tk):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = fn.get_lonlat(tk.lon, tk.lat)
        value = [b'U', 4, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid + \
                [tk.type, tk.bat, tk.ts, lon, lat, tk.alt, tk.speed, tk.course,
                 tk.gps, tk.acc, tk.gsm, tk.temp]
        self.logging.info("realtime_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_realtime(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [0, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("realtime_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_illegalShake(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [1, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("illegalShake_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_powerLow(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [2, 1, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("powerLow_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_fullEnerge(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [3, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("fullEnerge_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_emergency(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [4, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("emergency_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_status(self, seq, iccid, sessionID, t_time):
        lon, lat = self.get_lonlat()
        alt = 50
        speed = 120
        report_mg = [b'U', 4, 48, seq, sessionID] + iccid + [5, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]

        fmt = '!sBBBQ10B'
        fmt += 'BBiiihBBBBBb'
        lat = 114.965 * 100000
        lon = 22.972 * 100000
        alt = 50
        speed = 120
        value = [b'U', 4, 48, seq, sessionID] + iccid + [5, 100, t_time, lon, lat, alt, speed, 10, 20, 30, 4, -7]
        self.logging.info("status_mg: %s", value)
        report_mg = struct.pack(fmt, *value)
        return report_mg

    def compose_multi_pvts(self, seq, iccid, sessionID, t_time):
        lon, lat = self.get_lonlat()
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBhhh'
        speed = 13
        pdt = 95
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 28, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1, 10056, 803]
        self.logging.info("multi_pvt_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_stop(self, tk, ts=None):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        status = 1
        ts = ts or int(time.time())
        value = [b'U', 5, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid + \
                [1, 24, int(ts), int(tk.lon*100000), int(tk.lat*100000),
                 tk.alt, tk.speed, tk.course, tk.gps,
                 tk.acc, tk.gsm, tk.temp, tk.bat, status, 1]
        self.logging.info("stop_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_move(self, tk, lonlats):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh' * len(lonlats)
        value = [b'U', 5, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid + [len(lonlats), 24]
        for i, l in enumerate(lonlats):
            if i == 0:
                status = 2
            else:
                status = 0
            value += [int(l[2]), int(l[0]), int(l[1]),
                      tk.alt, tk.speed, tk.course, tk.gps,
                      tk.acc, tk.gsm, tk.temp, tk.bat, status, 1]
        self.logging.info("move_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_stopcharging(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lon, lat = self.get_lonlat()
        speed = 13
        pdt = 95
        status = 3
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("stopcharging_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_charging(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lon, lat = self.get_lonlat()
        speed = 13
        pdt = 95
        status = 4
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("charging_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_overspeed(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lon, lat = self.get_lonlat()
        speed = 150
        pdt = 89
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("overspeed_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_enterRegion(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lat = 110396808 / 36
        lon = 374520744 / 36
        speed = 100
        pdt = 89
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("enterRegion_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_leaveRegion(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lat = 110396808 / 36
        lon = 374513184 / 36
        speed = 100
        pdt = 89
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("leaveRegion_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_u6(self, tk, info):
        fmt = '!sBBBQ10B'
        length = len(info)
        fmt += 'iH%ss' % length
        value = [b'U', 6, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid + [int(time.time()), length, info.encode('utf-8')]
        self.logging.info("u6_mg: %s", value)
        u6_mg = struct.pack(fmt, *value)
        return u6_mg

    def fmt_mac(self, mac):
        return list(struct.unpack('!6B', binascii.a2b_hex(mac)))

    def fmt_temp(self, temp):
        temp = float('%.2f' % temp)
        temp1, temp2 = str(temp).split('.')
        if len(temp2) == 1 and int(temp2) != 0:
            temp2 = int(temp2) * 10
        if int(temp1) < 0:
            temp1 = abs(int(temp1)) | 0x80

        return [int(temp1), int(temp2)]

    def compose_u7_header(self, tk, l):
        fmt = '!sBBBQ10BB'
        value = [b'U', 7, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid + [l]
        return value, fmt

    def compose_ruuvi(self, ruuvi, value, fmt):
        fmt += 'BBi6BBBBB' * len(ruuvi)
        for r in ruuvi:
            ts = r.ts or int(time.time())
            temp = self.fmt_temp(r.temp)
            mac = self.fmt_mac(r.mac)
            v = [1, r.rssi, ts] + mac + [r.bat, r.hum*2] + temp
            value.extend(v)
        return value, fmt

    def compose_wireless_door(self, door, value, fmt):
        fmt += 'BBi6BBBBB' * len(door)
        for r in door:
            ts = r.ts or int(time.time())
            mac = self.fmt_mac(r.mac)
            v = [2, r.rssi, ts] + mac + [r.bat, r.status, r.c2o_ts, r.o2c_ts]
            value.extend(v)
        return value, fmt

    def compose_range(self, range, value, fmt):
        fmt += 'BBi6BBBh' * len(range)
        for r in range:
            ts = r.ts or int(time.time())
            mac = self.fmt_mac(r.mac)
            v = [3, r.rssi, ts] + mac + [r.bat, r.status, r.value]
            value.extend(v)
        return value, fmt

    def compose_u8(self, tk):
        t_time = int(time.time())
        fmt = '!sBBBQ10B'
        fmt += 'BBIiihBBBBBbHHIBBI6B'
        lon, lat = fn.get_lonlat(tk.lon, tk.lat)
        rxlev = 39
        tp = -5
        bvg = 3200
        epvg = 800
        ait = t_time - 100
        blet = 3
        bler = 88
        blets = t_time - 90
        blemac = [209, 58, 39, 178, 72, 129]
        value = [b'U', 8, 48, fn.get_seq(tk.sn), tk.sessionID] + tk.fmt_iccid
        value += [0, 86, t_time, lon, lat, tk.alt, tk.speed,
                  tk.course, tk.gps, tk.acc, rxlev,
                  tp, bvg, epvg, ait, blet, bler, blets] + blemac
        self.logging.info("u8_msg: %s", value)
        u8_mg = struct.pack(fmt, *value)
        return u8_mg
