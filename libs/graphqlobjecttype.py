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


class WiredSensorType(graphene.Enum):
    gpio0 = 'GPIO0'
    gpio1 = 'GPIO1'
    gpio2 = 'GPIO2'
    gpio3 = 'GPIO3'
    gpio4 = 'GPIO4'
    gpio5 = 'GPIO5'


class WirelessSensorType(graphene.Enum):
    ruuvi = 1
    door = 2
    range = 3


class BaseWirelessSensorObject(graphene.InputObjectType):
    mac = graphene.Argument(graphene.String, required=True)
    bat = graphene.Argument(graphene.Int, default_value=82)
    rssi = graphene.Argument(graphene.Int, default_value=70)
    ts = graphene.Argument(graphene.Int)


class RuuviSensorObject(BaseWirelessSensorObject):
    temp = graphene.Argument(graphene.Float, required=True)
    hum = graphene.Argument(graphene.Int, required=True)


class DoorSensorObject(BaseWirelessSensorObject):
    status = graphene.Argument(graphene.Int, required=True)
    c2o_ts = graphene.Argument(graphene.Int, default_value=255)
    o2c_ts = graphene.Argument(graphene.Int, default_value=255)


class RangeSensorObject(BaseWirelessSensorObject):
    status = graphene.Argument(graphene.Int, default_value=0)
    value = graphene.Argument(graphene.Int, required=True)


class WiredSensorObject(graphene.InputObjectType):
    gpiox = graphene.Argument(WiredSensorType, required=True)
    offset = graphene.Argument(graphene.Int, default_value=15)
    value = graphene.Argument(graphene.Int, required=True)

