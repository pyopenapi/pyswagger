from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import (
    DataTypeObj
)
import six


class ConvertString(object):

    class Disp(Dispatcher): pass

    @Disp.register([DataTypeObj])
    def _covert(self, name, obj):
        if obj.defaultValue != None:
            pass

        def _conver_from_string(name, val):
            if name == 'double' or name == 'float':
                return float(val)
            elif name == 'integer' or name == 'long':
                # those example always set min & max to float
                return int(float(val))
            return val

        if isinstance(obj.minimum, six.string_types):
            # TODO: float or double or int or long
            obj.update_field('minimum', _conver_from_string(obj.type, obj.minimum))
        if obj.maximum != None:
            obj.update_field('maximum', _conver_from_string(obj.type, obj.maximum))

