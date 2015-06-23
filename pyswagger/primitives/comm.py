from __future__ import absolute_import
from ..errs import ValidationError
import json


class PrimJSONEncoder(json.JSONEncoder):
    """ json encoder for primitives
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)

def min_max(obj, val, is_max):
    """ min/max validator for float and integer
    """
    n = getattr(obj, 'maximum' if is_max else 'minimum', None)
    if n == None:
        return

    _eq = getattr(obj, 'exclusiveMaximum' if is_max else 'exclusiveMinimum', False)
    if is_max:
        to_raise = val >= n if _eq else val > n
    else:
        to_raise = val <= n if _eq else val < n

    if to_raise:
        raise ValidationError('condition failed: {0}, v:{1} compared to o:{2}'.format('maximum' if is_max else 'minimum', val, n))

#
# creater/2nd_pass function with python user defined class
# - Array
# - Model
# - Byte
# - Datetime
# - Date
# - File
#
def _2nd_pass_obj(obj, ret, val, ctx):
    return ret.apply_with(obj, val, ctx) 

def create_obj(obj, v, ctx=None, constructor=None):
    return constructor()

