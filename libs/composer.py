# -*- coding: utf-8 -*-
import binascii
import struct
import random

import logging
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
                 ] + iccid + [args.bat, args.chg, args.gms, args.temp, 0, 0]
        self.logging.info("realtime_mg: %s", value)
        heartbeat_mg = struct.pack(fmt, *value)
        return heartbeat_mg

    def compose_config(self, seq, iccid, sessionID):
        fmt = '!sBBBQ10B'
        value = [b'U', 3, 48, seq, sessionID] + iccid
        self.logging.info("config_mg: %s", value)
        config_mg = struct.pack(fmt, *value)
        return config_mg

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

    def compose_stop(self, seq, iccid, sessionID, t_time):
        lon, lat = self.get_lonlat()
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        speed = 13
        pdt = 95
        status = 1
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("stop_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_move(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lon, lat = self.get_lonlat()
        speed = 13
        pdt = 95
        status = 2
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
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

    def compose_enterPOI(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lat = 110396808 / 36
        lon = 374540184 / 36
        speed = 100
        pdt = 90
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("enterPOI_mg: %s", value)
        position_mg = struct.pack(fmt, *value)
        return position_mg

    def compose_leavePOI(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10BBB'
        fmt += 'iiihBBBBBbBBh'
        lat = 110396808 / 36
        lon = 374530824 / 36
        speed = 100
        pdt = 89
        status = 0
        value = [b'U', 5, 48, seq, sessionID] + iccid + [1, 24, t_time, lon, lat, 20, speed, 10, 25, 30, 9, 1, pdt, status, 1]
        self.logging.info("leavePOI_mg: %s", value)
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

    def compose_u6(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        info = 'TEMP@15=100|GPIO1@15=31|GPIO2@15=1384|DOR@10=1|ODO@26=206825|FUL@26=15|RPM@26=890'
        length = len(info)
        fmt += 'iH%ss' % length
        value = [b'U', 6, 48, seq, sessionID] + iccid + [t_time, length, info]
        self.logging.info("u6_mg: %s", value)
        u6_mg = struct.pack(fmt, *value)
        return u6_mg

    def compose_u8(self, seq, iccid, sessionID, t_time):
        fmt = '!sBBBQ10B'
        fmt += 'BBIiihBBBBBbHHIBBI6B'
        lng, lat = self.get_lonlat()
        alt = 12
        speed = 60
        cs = 10
        gps = 45
        pacc = 23
        rxlev = 39
        tp = -5
        bvg = 3200
        epvg = 800
        ait = t_time - 100
        blet = 3
        bler = 88
        blets = t_time - 90
        blemac = [209, 58, 39, 178, 72, 129]
        value = [b'U', 8, 48, seq, sessionID] + iccid
        value += [0, 86, t_time, lng, lat, alt, speed, cs, gps, pacc, rxlev,
                  tp, bvg, epvg, ait, blet, bler, blets] + blemac
        self.logging.info("u8_msg: %s", value)
        u8_mg = struct.pack(fmt, *value)
        return u8_mg
