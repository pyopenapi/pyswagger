from __future__ import absolute_import
from .utils import from_iso8601, none_count
import datetime
import functools
import six
import base64
import json


class Byte(object):
    """
    """
    def __init__(self, _, v):
        if isinstance(v, six.string_types):
            self.v = v
        else:
            raise ValueError('Unsupported type for Byte: ' + str(type(v)))

    def __str__(self):
        return self.v

    def to_json(self):
        """ according to https://github.com/wordnik/swagger-spec/issues/50,
        we should exchange 'byte' type via base64 encoding.
        """
        return base64.urlsafe_b64encode(self.v)


class Time(object):
    """ Base of Datetime & Date
    """
    def __str__(self):
        return str(self.to_json())

    def to_json(self):
        # according to
        #   https://github.com/wordnik/swagger-spec/issues/95
        return self.isoformat()


class Date(Time):
    """
    """
    def __init__(self, _, v):
        self.v = None
        if isinstance(v, float):
            self.v = datetime.date.fromtimestamp(v)
        elif isinstance(v, datetime.date):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = from_iso8601(v).date()
        else:
            raise ValueError('Unrecognized type for Date: ' + str(type(v)))


class Datetime(Time):
    """
    """
    def __init__(self, _, v):
        self.v = None
        if isinstance(v, float):
            self.v = datetime.datetime.fromtimestamp(v)
        elif isinstance(v, datetime.datetime):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = from_iso8601(v)
        else:
            raise ValueError('Unrecognized type for Datetime: ' + str(type(v)))


class Array(list):
    """
    """
    def __init__(self, item_type, v, unique=False):
        """ v: list or string_types
        """
        super(Array, self).__init__()

        if isinstance(v, six.string_types):
            v = json.loads(v)

        # init array as list
        v = set(v) if unique else v
        self.extend(map(functools.partial(prim_factory, item_type, multiple=False), v))

    def __str__(self):
        s = ''
        for v in self:
            s = ''.join([s, ',' if s else '', str(v)])
        return s


class Model(dict):
    """
    """

    # access dict like object
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, obj, val):
        """ val: dict or string_types
        """
        super(Model, self).__init__()

        if isinstance(val, six.string_types):
            val = json.loads(val)
        elif isinstance(val, six.binary_type):
            # TODO: encoding problem...
            val = json.loads(val.decode('utf-8'))

        cur = obj
        while cur != None:
            # init model as dict
            for k, v in six.iteritems(cur.properties):
                to_update = val.get(k, None)

                # update discriminator with model's id
                if cur.discriminator and cur.discriminator == k:
                    to_update = obj.id

                # check require properties of a Model
                if to_update == None:
                    if cur.required and k in cur.required:
                        raise ValueError('Model:[' + str(cur.id) + '], require:[' + str(k) + ']')

                self[k] = prim_factory(v, to_update)

            cur = cur._extends_

    def __eq__(self, other):
        if other == None:
            return False

        for k, v in six.iteritems(self):
            if v != other.get(k, None):
                return False

        residual = set(other.keys()) - set(self.keys())
        for k in residual:
            if other[k] != None:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_json(self):
        """ strip None values before sending on the wire """
        # only when regenerate an dict is effective enough
        if none_count(self) * 10 / len(self.keys()) < 3:
            return self

        ret = {}
        for k, v in six.iteritems(self):
            if v == None:
                continue
            ret.update({k: v})
        return ret


class Void(object):
    """
    """
    def __init__(self, _, v):
        pass

    def __eq__(self, v):
        return v == None

    def __str__(self):
        return ''

    def to_json(self):
        return None


class File(object):
    """
    """
    def __init__(self, obj, val):
        """
        header:
            Content-Type -> content-type
            Content-Transfer-Encoding -> content-transder-encoding
        filename -> name
        file-like object or path -> data
        """
        self.header = val.get('header', {})
        self.data = val.get('data', None)
        self.filename = val.get('filename', '')


class PrimJSONEncoder(json.JSONEncoder):
    """
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)

def create_numeric(obj, v, t):
    # truncate based on min/max
    if obj.minimum and v < obj.minimum:
        raise ValueError('below minimum: {0}, {1}'.format(v, obj.minimum))
    if obj.maximum and v > obj.maximum:
        raise ValueError('above maximum: {0}, {1}'.format(v, obj.maximum))
 
    return t(v)

def create_int(obj, v):
    return create_numeric(obj, v, int)

def create_float(obj, v):
    return create_numeric(obj, v, float)

def create_str(obj, v):
    if obj.enum and v not in obj.enum:
        raise ValueError('{0} is not a valid enum for {1}'.format(v, str(obj.enum)))

    return str(v)

# refer to 4.3.1 Primitives in v1.2
prim_obj_map = {
    # int
    ('integer', 'int32'): create_int,
    ('integer', 'int64'): create_int,

    # float
    ('number', 'float'): create_float,
    ('number', 'double'): create_float,

    # str
    ('string', ''): create_str,
    ('string', None): create_str,

    ('string', 'byte'): Byte,
    ('string', 'date'): Date,
    ('string', 'date-time'): Datetime,

    # bool
    ('boolean', ''): bool,
    ('boolean', None): bool,

    # File
    ('File', ''): File,
    ('File', None): File,

    # void
    ('void', ''): Void,
    ('void', None): Void,
};


prim_types = [
    'integer',
    'number',
    'string',
    'boolean',
    'void',
    'File',
    'array',
]

def prim_factory(obj, v, multiple=False):
    """
    """
    v = obj.defaultValue if v == None else v
    if v == None:
        return None

    # wrap 'allowmultiple' date with array
    if multiple and obj.type != 'array' and isinstance(v, (tuple, list)):
        return Array(obj, v, unique=False);

    if obj.ref:
        return obj.ref._prim_(v)
    elif isinstance(obj.type, six.string_types):
        if obj.type == 'array':
            return Array(obj.items, v, unique=obj.uniqueItems)
        else:
            t = prim_obj_map.get((obj.type, obj.format), None)
            if not t:
                raise ValueError('Can\'t resolve type from:(' + str(obj.type) + ', ' + str(obj.format) + ')')

            return t(obj, v)

    else:
        # obj.type is a reference to a Model
        return obj.type._prim_(v)

def is_primitive(obj):
    """ check if a given object refering to a primitive
    defined in spec.
    """
    return obj.type in prim_types

