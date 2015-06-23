from __future__ import absolute_import
from .comm import min_max


def validate_int(obj, ret, val, ctx):
    min_max(obj, ret, False)
    min_max(obj, ret, True)

    return val
 
def create_int(obj, v, ctx=None):
    r = int(v)
    validate_int(obj, r, v, ctx)
    return r

