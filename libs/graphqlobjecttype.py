# -*- coding: utf-8 -*-
import graphene


class Result(graphene.ObjectType):
    code = graphene.Int()
    message = graphene.String()


class ChargingStatus(graphene.Enum):
    NO = 0
    YES = 1
    CON = 2
