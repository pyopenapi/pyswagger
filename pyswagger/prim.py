from __future__ import absolute_import
from .utils import from_iso8601
import datetime
import functools
import six
import base64
import json


class Primitive(object):
    """ base of all overrided primitives
    """
    def __str__(self):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()


class Byte(Primitive):
    """
    """
    def __init__(self, v):
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


class Time(Primitive):
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
    def __init__(self, v):
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
    def __init__(self, v):
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

        # init model as dict
        for k, v in obj.properties.iteritems():
            to_update = val.get(k, None)

            # check require properties of a Model
            if to_update == None:
                if k in obj.required:
                    raise ValueError('Model:[' + str(obj.id) + '], require:[' + str(k) + ']')
                continue

            self[k] = prim_factory(v, to_update)


class Void(object):
    """
    """
    def __init__(self, v):
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
    def __init__(self, val):
        pass


class PrimJSONEncoder(json.JSONEncoder):
    """
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


# refer to 4.3.1 Primitives in v1.2
prim_obj_map = {
    # int
    ('integer', 'int32'): int,
    ('integer', 'int64'): int,

    # float
    ('number', 'float'): float,
    ('number', 'double'): float,

    # str
    ('string', ''): str,
    ('string', None): str,

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
        elif obj.type == 'File':
            return File(v)
        else:
            t = prim_obj_map.get((obj.type, obj.format), None)
            if not t:
                raise ValueError('Can\'t resolve type from:(' + str(obj.type) + ', ' + str(obj.format) + ')')

            return t(v)

    else:
        # obj.type is a reference to a Model
        return obj.type._prim_(v)

def is_primitive(obj):
    """ check if a given object refering to a primitive
    defined in spec.
    """
    return obj.type in prim_types

