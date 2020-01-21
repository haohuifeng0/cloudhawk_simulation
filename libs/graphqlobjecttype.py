# -*- coding: utf-8 -*-
import graphene


class Result(graphene.ObjectType):
    code = graphene.Int()
    message = graphene.String()


class ChargingStatus(graphene.Enum):
    NO = 0
    YES = 1
    CON = 2


class AlertType(graphene.Enum):
    illegalShake = 1
    powerLow = 2
    powerFull = 3
    SOS = 4
    powerOutages = 6
