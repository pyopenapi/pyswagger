from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import DataTypeObj, Items, Model
from ..utils import scope_split, scope_compose
from ..prim import is_primitive
import weakref
import six


class Resolve(object):
    """
    """
    class Disp(Dispatcher): pass

    @Disp.register([Items, DataTypeObj])
    def _resolve(self, scope, name, obj, app):
        """ resolve ref to models """
        to_resolve = None
        if isinstance(obj.ref, six.string_types):
            to_resolve = 'ref'
        elif isinstance(obj.type, six.string_types) and not is_primitive(obj):
            to_resolve = 'type'
        else:
            # already resolved.
            return

        # looking for name of resource's scope
        r = scope_split(scope)[0]
        if not r:
            raise Exception('All DataType Object or Items should be enclosed in one scope')

        # compose the model's scope name and
        # try to load the model 
        obj.update_field(to_resolve, weakref.proxy(app.m[scope_compose(r, getattr(obj, to_resolve))]))

