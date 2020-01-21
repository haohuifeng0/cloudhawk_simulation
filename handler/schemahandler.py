# -*- coding: utf-8 -*-
from handler.mutationhandler import *


class Query(graphene.ObjectType):

    list = graphene.List(graphene.String)

    def resolve_tracker(self, info):
        return {'ok': 'ok'}


class Mutation(graphene.ObjectType):
    class Meta:
        description = (
            "Del operations may return null if the sensor with the given "
            "`id` doesn't exist (or not belong to the tracker)."
        )

    add = Add.Field()
    delete = Del.Field()
    set = Set.Field()
    alert = SetAlert.Field()


schema = graphene.Schema(Query, Mutation)
