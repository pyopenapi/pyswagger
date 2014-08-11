from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import DataTypeObj, Items, Model
from ..utils import scope_split, scope_compose
import weakref


class Resolve(object):
    """
    """
    class Disp(Dispatcher): pass

    @Disp.register([Items, DataTypeObj])
    def _resolve(self, scope, name, obj, app):
        """ resolve ref to models """
        if obj.ref == None:
            return
        elif isinstance(obj.ref, Model):
            # already resolved.
            return

        # looking for name of resource's scope
        r = scope_split(scope)[0]
        if not r:
            raise Exception('All DataType Object or Items should be enclosed in one scope')

        # compose the model's scope name and
        # try to load the model 
        try:
            obj.update_field('ref', weakref.proxy(app.m[scope_compose(r, obj.ref)]))
        except Exception as e:
            raise e
            # TODO: log
            raise Exception('Unable to resovle this ref: ' + str(scope) + ', name:' + str(name) + ', ref:' + str(obj.ref))

