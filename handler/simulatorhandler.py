# -*- coding: utf-8 -*-
import threading
import time
import logging
import re
import socket

from tornado.ioloop import IOLoop

import json

from tornado.options import options

from libs import fn
from libs.composer import Composer
from libs.parser import Parser


class SimulatorTracker(object):
    # 3.3
    def __init__(self, sn, iccid, socket_param, lon=104.03974, lat=30.66578):
        self.sn = sn
        self.iccid = iccid
        self.logging = logging
        self.seq = 0

        iccid_lst = re.findall(r'(.{2})', self.iccid)
        self.iccid_lst_int = []
        for item in iccid_lst:
            self.iccid_lst_int.append(int(item, 16))
        sn_lst = re.findall(r'(.{2})', self.sn)
        self.sn_lst_int = []
        for item in sn_lst:
            self.sn_lst_int.append(int(item, 16))

        self.socket = socket_param
        self.res = dict()
        self.composer = Composer(lon, lat)
        self.first_login = False

    def send_login(self):
        T1 = self.composer.compose_login(fn.get_seq(self.sn), self.sn_lst_int, self.iccid_lst_int)
        self.socket.send(T1)

    def send_heartbat(self):
        while True:
            if options.tracker.get(self.sn):
                U2 = self.composer.compose_heartbat(fn.get_seq(self.sn),
                                                    self.iccid_lst_int,
                                                    options.tracker[self.sn])
                self.socket.send(U2)
            else:
                break
            time.sleep(1.8e3)

    def send_config(self):

        U3 = self.composer.compose_config(fn.get_seq(self.sn), self.iccid_lst_int,
                                          int(self.res['sessionID']))
        self.socket.send(U3)

    def send_realtime(self, t_time, sessionID):
        U4 = self.composer.compose_realtime(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_multi_pvts(self, t_time, sessionID):
        U5 = self.composer.compose_multi_pvts(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_illegalShake(self, t_time, sessionID):
        U4 = self.composer.compose_illegalShake(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_powerLow(self, t_time, sessionID):
        U4 = self.composer.compose_powerLow(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_fullEnerge(self, t_time, sessionID):
        U4 = self.composer.compose_fullEnerge(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_emergency(self, t_time, sessionID):
        U4 = self.composer.compose_emergency(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_status(self, t_time, sessionID):
        U4 = self.composer.compose_status(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U4)

    def send_move(self, t_time, sessionID):
        U5 = self.composer.compose_move(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_stopcharging(self, t_time, sessionID):
        U5 = self.composer.compose_stopcharging(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_charging(self, t_time, sessionID):
        U5 = self.composer.compose_charging(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_overspeed(self, t_time, sessionID):
        U5 = self.composer.compose_overspeed(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_enterPOI(self, t_time, sessionID):
        U5 = self.composer.compose_enterPOI(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_leavePOI(self, t_time, sessionID):
        U5 = self.composer.compose_leavePOI(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_enterRegion(self, t_time, sessionID):
        U5 = self.composer.compose_enterRegion(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_leaveRegion(self, t_time, sessionID):
        U5 = self.composer.compose_leaveRegion(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_stop(self, t_time, sessionID):
        U5 = self.composer.compose_stop(self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U5)

    def send_u6(self, sessionID, t_time):
        U6 = self.composer.compose_u6(
            self.get_seq(), self.iccid_lst_int, sessionID, t_time)
        self.socket.send(U6)

    def send_check(self, sessionID):
        U8 = self.composer.compose_u8(
            self.get_seq(), self.iccid_lst_int, sessionID, int(time.time()))
        self.socket.send(U8)

    def multi_u6(self, iccid):
        while True:
            self.send_u6(int(self.res['sessionID']), int(time.time()))
            time.sleep(30)

    def login(self, iccid, isFirst=True):
        self.send_login()
        self.first_login = isFirst

    def simulator_multi_pvts(self, iccid):
        while True:
            for i in range(30):
                self.send_multi_pvts(int(time.time()), int(self.res['sessionID']))
                self.logging.info("%s, multi_pvt send success!", iccid)
                time.sleep(10)
            self.seq += 1
            self.send_stop(int(self.res['sessionID']), int(time.time()))
            self.logging.info("%s, stop send success!", iccid)
            time.sleep(15)

    def tcpClient(self, iccid):
        try:
            self.login(iccid)
            parser = Parser()
            while True:
                dat = self.socket.recv(1024)
                if dat:
                    bp = parser.parse_base(dat)
                    self.handle_recv(bp, iccid, dat)
        except Exception as e:
            self.logging.error("What's wrong, reconnect it.")

    def handle_recv(self, bp, iccid, dat):
        parser = Parser()
        p_type = bp.header.cmd_type + bp.header.cmd_num
        success = bp.header['success']
        if int(success) == 0:
            if p_type == "D1":
                lp = parser.parse_login(dat)
                self.login_status = lp.data['login_status']
                if int(self.login_status) == 0:
                    self.res['sessionID'] = int(lp.data['sessionID'])
                    options.thread_lock.acquire()
                    options.tracker[self.sn]['sessionID'] = self.res['sessionID']
                    options.thread_lock.release()
                    self.logging.info("%s, login send success!", iccid)
                    self.send_config()
                    if self.first_login:
                        threading.Thread(target=self.send_heartbat).start()

            elif p_type == 'D3':
                lp = parser.parse_config(dat)
                print(lp.data)
        else:
            if p_type != "D1":
                self.logging.info("%s, status is offline!", iccid)
                self.login(iccid, False)
            else:
                self.logging.info("%s, login failed!", iccid)
