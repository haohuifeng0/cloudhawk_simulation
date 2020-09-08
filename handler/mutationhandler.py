# -*- coding: utf-8 -*-
import logging
import struct
import threading
import time
from threading import Thread

import graphene
from tornado.options import options

from handler.simulatorhandler import SimulatorTracker
from libs import RESPONSE, fn
from libs.composer import Composer
from libs.dotdict import DotDict
from libs.graphqlobjecttype import Result, ChargingStatus, AlertType, \
    RuuviSensorObject, DoorSensorObject, RangeSensorObject, WiredSensorType, WiredSensorObject


class Add(graphene.Mutation):

    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        iccid = graphene.Argument(graphene.String, required=True)

    Output = Result

    def mutate(self, info, sn, iccid):
        if options.tracker.get(sn):
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_EXISTS)
        else:

            options.tracker[sn] = DotDict(iccid=iccid, lon=-75.59302,
                                          lat=41.40672, seq=0,
                                          bat=20, temp=10,
                                          chg=0, gsm=9, speed=80,
                                          course=10, gps=20, acc=10,
                                          sn=sn, fmt_iccid=fn.fmt_iccid(iccid),
                                          alt=50
                                          )
            Thread(target=SimulatorTracker(
                sn, iccid, options.socket_param).tcpClient, args=(iccid, )).start()

            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        return Result(code=code, message=message)


class Del(graphene.Mutation):

    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)

    Output = Result

    def mutate(self, info, sn):
        if options.tracker.get(sn):
            options.tracker.pop(sn)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)


class Set(graphene.Mutation):

    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        temp = graphene.Argument(graphene.Int)
        bat = graphene.Argument(graphene.Int)
        chg = graphene.Argument(ChargingStatus)
        gsm = graphene.Argument(graphene.Int)
        acc = graphene.Argument(graphene.Int)

    Output = Result

    def mutate(self, info, sn, chg=None, bat=None, temp=None, gsm=None, acc=None):
        tk = options.tracker.get(sn)

        def _set_conf(args):
            for k in args:
                if args[k] is not None:
                    tk[k] = args[k]
        if tk:
            if any([chg, bat, temp, gsm, acc]):
                options.thread_lock.acquire()
                list(map(_set_conf, [{'chg': chg},
                                     {'bat': bat},
                                     {'temp': temp},
                                     {'acc': acc}]))
                options.thread_lock.release()
                u2 = Composer(tk.lon, tk.lat).compose_heartbat(fn.get_seq(sn), fn.fmt_iccid(tk.iccid), tk)
                options.socket_param.send(u2)

            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)


class SetAlert(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        type = graphene.Argument(AlertType, required=True)
        bat = graphene.Argument(graphene.Int)
        ts = graphene.Argument(graphene.Int)
        lon = graphene.Argument(graphene.Float)
        lat = graphene.Argument(graphene.Float)
        alt = graphene.Argument(graphene.Int)
        speed = graphene.Argument(graphene.Int)
        course = graphene.Argument(graphene.Int)
        gps = graphene.Argument(graphene.Int)
        acc = graphene.Argument(graphene.Int)
        gsm = graphene.Argument(graphene.Int)
        temp = graphene.Argument(graphene.Int)

    Output = Result

    def mutate(self, info, sn, type, bat=None, ts=int(time.time()),
               temp=None, gsm=None, acc=None, gps=None, course=None,
               speed=None, alt=None, lon=None, lat=None):
        tk = options.tracker.get(sn)

        def _set_conf(args):
            for k in args:
                if args[k] is not None:
                    tk[k] = args[k]
        if tk:
            options.thread_lock.acquire()
            list(map(_set_conf, [{'type': type},
                                 {'bat': bat},
                                 {'temp': temp},
                                 {'ts': ts},
                                 {'gsm': gsm},
                                 {'gps': gps},
                                 {'course': course},
                                 {'speed': speed},
                                 {'alt': alt},
                                 {'lon': lon},
                                 {'lat': lat},
                                 {'acc': acc}]))
            options.thread_lock.release()
            u4 = Composer(tk.lon, tk.lat).compose_u4(tk)
            options.socket_param.send(u4)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)


class Move(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        lonlats = graphene.Argument(graphene.List(graphene.List(graphene.Float)), required=True)
        speed = graphene.Argument(graphene.Int)
        last_stop = graphene.Argument(graphene.Boolean)

    Output = Result

    def mutate(self, info, sn, lonlats, speed=None, last_stop=False):
        tk = options.tracker.get(sn)
        ts = int(time.time())

        if tk:
            error_lons = []
            error_lats = []
            for i, t in enumerate(lonlats):
                if t[0] > 180 or t[0] < -180:
                    error_lons.append(t[0])
                if t[1] > 90 or t[1] < -90:
                    error_lats.append(t[1])
                lonlats[i][0] *= 100000
                lonlats[i][1] *= 100000
                if len(lonlats[i]) == 2:
                    lonlats[i].append(ts)
                    ts += 10

            if error_lats or error_lons:
                return Result(code=RESPONSE.ILLEGAL_FORMAT,
                              message='经度或纬度超出范围, '
                                      '经度: %s; 纬度: %s' % (error_lons, error_lats))
            else:
                options.thread_lock.acquire()
                tk['lon'] = lonlats[-1][0]/100000
                tk['lat'] = lonlats[-1][1]/100000
                if speed is not None:
                    tk['speed'] = speed
                options.thread_lock.release()
            u5 = Composer(tk.lon, tk.lat).compose_move(tk, lonlats)
            options.socket_param.send(u5)
            if last_stop:
                ts = lonlats[-1][2]+2
                threading.Timer(ts, options.socket_param.send,
                                args=(Composer(tk.lon, tk.lat).compose_stop(tk, ts=ts)))
                # u5 = Composer(tk.lon, tk.lat).compose_stop(tk)
                # options.socket_param.send(u5)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)


class Stop(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        ts = graphene.Argument(graphene.Int)

    Output = Result

    def mutate(self, info, sn, ts=None):
        tk = options.tracker.get(sn)

        if tk:
            u5 = Composer(tk.lon, tk.lat).compose_stop(tk, ts=ts)
            options.socket_param.send(u5)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)


class WiredSensor(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        wireds = graphene.Argument(graphene.List(WiredSensorObject), required=True)

    Output = Result

    def mutate(self, info, sn, wireds):
        tk = options.tracker.get(sn)

        if tk:
            cp = Composer(tk.lon, tk.lat)
            info = ''
            for d in wireds:
                if info:
                    info += '|'
                info += d['gpiox'] + '@' + str(d['offset']) + '=' + str(d['value'])
            msg = cp.compose_u6(tk, info)
            options.socket_param.send(msg)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)

        return Result(code=code, message=message)


class WirelessSensor(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        ruuvi = graphene.Argument(graphene.List(RuuviSensorObject), default_value=[])
        door = graphene.Argument(graphene.List(DoorSensorObject), default_value=[])
        range = graphene.Argument(graphene.List(RangeSensorObject), default_value=[])

    Output = Result

    def mutate(self, info, sn, ruuvi, door, range):
        tk = options.tracker.get(sn)

        if tk:
            cp = Composer(tk.lon, tk.lat)
            lth = len(ruuvi) + len(range) + len(door)
            value, fmt = cp.compose_u7_header(tk, lth)
            if ruuvi:
                value, fmt = cp.compose_ruuvi(ruuvi, value, fmt)
            if door:
                value, fmt = cp.compose_wireless_door(door, value, fmt)
            if range:
                value, fmt = cp.compose_range(range, value, fmt)
            msg = struct.pack(fmt, *value)
            logging.info("u7_mg: %s", value)
            options.socket_param.send(msg)

            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)

        return Result(code=code, message=message)


class SelfCheck(graphene.Mutation):
    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)

    Output = Result

    def mutate(self, info, sn):
        tk = options.tracker.get(sn)

        if tk:
            cp = Composer(tk.lon, tk.lat)
            msg = cp.compose_u8(tk)
            options.socket_param.send(msg)
            code, message = RESPONSE.fmt_response(RESPONSE.OK)
        else:
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_NOT_EXISTS)
        return Result(code=code, message=message)
