from __future__ import absolute_import
from ..scan import Dispatcher
from ..errs import SchemaError
from ..spec.v2_0.objects import Operation
from ..utils import scope_compose
from ..consts import private

class TypeReduce(object):
    """ Type Reducer, collect Operation & Model
    spreaded in Resources put in a global accessible place.
    """
    class Disp(Dispatcher): pass

    def __init__(self, sep=private.SCOPE_SEPARATOR):
        self.op = {}
        self.__sep = sep

    @Disp.register([Operation])
    def _op(self, path, obj, _):
        scope = obj.tags[0] if obj.tags and len(obj.tags) > 0 else None
        name = obj.operationId if obj.operationId else None

        # in swagger 2.0, both 'operationId' and 'tags' are optional.
        # When 'operationId' is empty, it causes 'scope_compose' return something
        # duplicated with other Operations with the same tag.
        if not name:
            return

        new_scope = scope_compose(scope, name, sep=self.__sep)
        if new_scope:
            if new_scope in self.op.keys():
                raise SchemaError('duplicated key found: ' + new_scope)

            self.op[new_scope] = obj

