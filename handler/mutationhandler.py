# -*- coding: utf-8 -*-
import time
from threading import Thread

import graphene
from tornado.options import options

from handler.simulatorhandler import SimulatorTracker
from libs import RESPONSE, fn
from libs.composer import Composer
from libs.dotdict import DotDict
from libs.graphqlobjecttype import Result, ChargingStatus, AlertType


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
