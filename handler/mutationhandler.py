# -*- coding: utf-8 -*-
import logging
import struct
import time
from threading import Thread

import graphene
from tornado.options import options

from handler.simulatorhandler import SimulatorTracker
from libs import RESPONSE, fn
from libs.composer import Composer
from libs.dotdict import DotDict
from libs.graphqlobjecttype import Result, ChargingStatus, AlertType, \
    RuuviSensorObject, DoorSensorObject, RangeSensorObject


class Add(graphene.Mutation):

    class Arguments:
        sn = graphene.Argument(graphene.String, required=True)
        iccid = graphene.Argument(graphene.String, required=True)

    Output = Result

    def mutate(self, info, sn, iccid):
        if options.tracker.get(sn):
            code, message = RESPONSE.fmt_response(RESPONSE.TRACKER_EXISTS)
        else:

            options.tracker[sn] = DotDict(iccid=iccid, lon=104.03974,
                                          lat=30.66578, seq=0,
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
                [_ for _ in map(_set_conf, [{'chg': chg},
                                            {'bat': bat},
                                            {'temp': temp},
                                            {'acc': acc}])]
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
            [_ for _ in map(_set_conf, [{'type': type},
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
                                        {'acc': acc}])]
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
        lons = graphene.Argument(graphene.List(graphene.Float), required=True)
        lats = graphene.Argument(graphene.List(graphene.Float), required=True)
        speed = graphene.Argument(graphene.Int)

    Output = Result

    def mutate(self, info, sn, lons, lats, speed=None):
        tk = options.tracker.get(sn)
        ts = int(time.time())

        if tk:
            if len(lons) != len(lats):
                return Result(code=RESPONSE.ILLEGAL_FORMAT, message='经度与纬度数量不匹配')
            lonlats = [x for x in zip(lons, lats)]
            error_lons = []
            error_lats = []
            for t in lonlats:
                if t[0] > 180 or t[0] < -180:
                    error_lons.append(t[0])
                if t[1] > 90 or t[1] < -90:
                    error_lats.append(t[1])
            if error_lats or error_lons:
                return Result(code=RESPONSE.ILLEGAL_FORMAT,
                              message='经度或纬度超出范围, '
                                      '经度: %s; 纬度: %s' % (error_lons, error_lats))

            if speed is not None:
                options.thread_lock.acquire()
                tk['speed'] = speed
                options.thread_lock.release()
            u4 = Composer(tk.lon, tk.lat).compose_move(tk, lonlats, ts)
            options.socket_param.send(u4)
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

