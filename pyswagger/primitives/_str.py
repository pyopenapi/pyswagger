from __future__ import absolute_import
from ..errs import ValidationError
from validate_email import validate_email


def validate_str(obj, ret, val, ctx):
    if obj.enum and ret not in obj.enum:
        raise ValidationError('{0} is not a valid enum for {1}'.format(ret, str(obj.enum)))
    if obj.maxLength and len(ret) > obj.maxLength:
        raise ValidationError('[{0}] is longer than {1} characters'.format(ret, str(obj.maxLength)))
    if obj.minLength and len(ret) < obj.minLength:
        raise ValidationError('[{0}] is shoter than {1} characters'.format(ret, str(obj.minLength)))

    # TODO: handle pattern
    return val

def create_str(obj, v, ctx=None):
    r = str(v)
    validate_str(obj, r, v, ctx)
    return r

def validate_email_(obj, ret, val, ctx):
    if not validate_email(ret):
        raise ValidationError('{0} is not a valid email for {1}'.format(ret, obj))

    return val
