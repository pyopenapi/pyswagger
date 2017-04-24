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

        # In Swagger 2.0 'operationId' is optional.
        # We need a name for 'scope_compose' so generate one if needed
        if obj.operationId:
            name = obj.operationId
        else:
            name_parts = [obj.method.upper()]

            if obj.base_path:
                name_parts.append(obj.base_path)

            name_parts.append(obj.path)

            name = ''.join(name_parts)

        new_scope = scope_compose(scope, name, sep=self.__sep)
        if new_scope:
            if new_scope in self.op.keys():
                raise SchemaError('duplicated key found: ' + new_scope)

            self.op[new_scope] = obj

