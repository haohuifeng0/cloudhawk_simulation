# -*- coding: utf-8 -*-
from copy import deepcopy


class _type_cls(dict):
    def __init__(self, t):
        dict.__init__(self, type=t)

    def __call__(self, **props):
        o = deepcopy(self)
        o.update(props)
        return o


class types:

    str = _type_cls('string')

    num = _type_cls('number')

    int = _type_cls('integer')

    null = _type_cls('null')

    bool = int(enum=[0, 1])

    @staticmethod
    def array(t, min_items=None, max_items=None):
        arr = {'type': 'array', 'items': t}
        if isinstance(min_items, int):
            assert min_items >= 0
            arr['minItems'] = min_items
        if isinstance(max_items, int):
            assert max_items >= 0
            arr['maxItems'] = max_items
        if 'minItems' in arr and 'maxItems' in arr:
            assert min_items <= max_items
        return arr

    @staticmethod
    def any_of(*ts):
        return {'anyOf': list(ts)}

    @staticmethod
    def all_of(*ts):
        return {'allOf': list(ts)}

    @staticmethod
    def one_of(*ts):
        return {'oneOf': list(ts)}
