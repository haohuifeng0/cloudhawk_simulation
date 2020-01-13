# -*- coding: utf-8 -*-
import graphene

from handler.mutationhandler import Add


class Query(graphene.ObjectType):

    tracker = graphene.List(graphene.String)

    def resolve_tracker(self, info):
        return {'ok': 'ok'}


class Mutation(graphene.ObjectType):
    class Meta:
        description = (
            "Del operations may return null if the sensor with the given "
            "`id` doesn't exist (or not belong to the tracker)."
        )

    add_wired = Add.Field()
