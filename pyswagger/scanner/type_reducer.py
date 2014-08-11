from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import Operation, Model
from ..utils import scope_compose


class TypeReduce(object):
    """ Type Reducer, collect Operation & Model
    spreaded in Resources put in a global accessible place.
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.op = {}
        self.model = {}

    @staticmethod
    def __insert(target, scope, name, obj):
        new_scope = scope_compose(scope, name)
        if new_scope in target.keys():
            raise ValueError('duplicated key found: ' + new_scope)

        target[new_scope] = obj

    @Disp.register([Model])
    def _model(self, scope, name, obj, _):
        self.__insert(self.model, scope, name, obj)

    @Disp.register([Operation])
    def _op(self, scope, name, obj, _):
        self.__insert(self.op, scope, name, obj)

