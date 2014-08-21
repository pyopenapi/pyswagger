from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import DataTypeObj, Items, Model, ResponseMessage
from ..utils import scope_split, scope_compose
from ..prim import is_primitive
import weakref
import six


class Resolve(object):
    """
    """
    class Disp(Dispatcher): pass

    @staticmethod
    def _find_and_update(to_resolve, scope, obj, app):
        """ helper function to find referenced model and update field
        """
        # looking for name of resource's scope
        r = scope_split(scope)[0]
        if not r:
            raise Exception('All DataType Object or Items should be enclosed in one scope')

        # compose the model's scope name and
        # try to load the model 
        obj.update_field(to_resolve, weakref.proxy(app.m[scope_compose(r, getattr(obj, to_resolve))]))

    @Disp.register([Items, DataTypeObj])
    def _resolve(self, scope, _, obj, app):
        """ resolve ref to models """
        to_resolve = None
        if is_primitive(obj):
            # normal type
            return
        elif isinstance(obj.ref, six.string_types):
            to_resolve = 'ref'
        elif isinstance(obj.type, six.string_types):
            to_resolve = 'type'
        elif isinstance(obj.ref, Model) or isinstance(obj.type, Model):
            # already resolved.
            return
        else:
            raise ValueError('Unknown object to resolve, ref:[' + str(obj.ref) + '], type:[' + str(obj.type) + ']')

        self._find_and_update(to_resolve, scope, obj, app)

    @Disp.register([ResponseMessage])
    def _resolve_resp_msg(self, scope, _, obj, app):
        """ resolve responseModel """
        if obj.responseModel == None or isinstance(obj.responseModel, Model):
            # already resolved
            return
        if not isinstance(obj.responseModel, six.string_types):
            raise ValueError('Unknown ResponseMessage\'s Model:[' +str(obj.responseModel) + ']')

        self._find_and_update('responseModel', scope, obj, app)      

