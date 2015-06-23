from __future__ import absolute_import
from ..errs import ValidationError
from .comm import min_max

def validate_float(obj, ret, val, ctx):
    min_max(obj, ret, False)
    min_max(obj, ret, True)
    if obj.multipleOf and ret % obj.multipleOf != 0:
        raise ValidationError('{0} should be multiple of {1}'.format(val, obj.multipleOf))

    return val

def create_float(obj, v, ctx=None):
    r = float(v)
    validate_float(obj, r, v, ctx)
    return r


