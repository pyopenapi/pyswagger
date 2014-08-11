from __future__ import absolute_import
from ..scan import Dispatcher
from ..obj import DataTypeObj, Parameter
import six


class Validate(object):
    """
    """
    class Disp(Dispatcher): pass

    @Disp.register([DataTypeObj])
    def _validate_data(self, scope, name, obj, _):
        """ convert string value to integer/float value """
        if obj.type == None and obj.ref == None:
            raise ValueError('type or $ref should be existed: ' + name + ', in scope:' + scope)

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
        if isinstance(obj.maximum, six.string_types):
            obj.update_field('maximum', _conver_from_string(obj.type, obj.maximum))

        # make sure there is 'item' along with 'array'
        if not (obj.type == 'array') == (obj.items != None):
            raise ValueError('array should be existed along with items')
        if obj.uniqueItems != None and obj.type != 'array':
            raise ValueError('uniqueItems is only used for array type.')


    @Disp.register([Parameter])
    def _validate_param(self, scope, name, obj, _):
        """ validate option combination of Parameter object """
        if obj.allowMultiple:
            if not obj.paramType in ('path', 'query', 'header'):
                pass
            if obj.type == 'array':
                raise NotImplementedError('array Type with allowMultiple is not implemented, in scope:' + scope)

        if obj.type == 'body' and obj.name not in ('', 'body'):
            raise ValueError('body parameter with invalid name: ' + obj.name + ', in scope:' + scope)

        if obj.type == 'File':
            if obj.paramType != 'form':
                raise ValueError('File parameter should be form type: ' + obj.name + ', in scope:' + scope)
            if 'multipart/form-data' not in obj._parent_.consumes:
                raise ValueError('File parameter should consume multipart/form-data: ' + obj.name + ', in scope:' + scope)

