# -*- coding: utf-8 -*-
import graphene


class Result(graphene.ObjectType):
    code = graphene.Int()
    message = graphene.String()


class Add(graphene.Mutation):
    Output = Result

    def mutate(self, info):
        return Result(code=0, message='ok')
