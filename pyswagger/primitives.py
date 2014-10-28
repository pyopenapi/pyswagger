from __future__ import absolute_import
from .utils import from_iso8601, none_count
import datetime
import functools
import six
import base64
import json


class Byte(object):
    """ for string type, byte format
    """

    def __init__(self, _, v):
        """ constructor

        :param str v: only accept six.string_types
        """
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
    """ for string type, date format
    """

    def __init__(self, _, v):
        """ constructor

        :param v: things used to constrcut date
        :type v: timestamp in float, datetime.date object, or ISO-8601 in str
        """
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
    """ for string type, datetime format
    """

    def __init__(self, _, v):
        """ constructor

        :param v: things used to constrcut date
        :type v: timestamp in float, datetime.datetime object, or ISO-8601 in str
        """
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
    """ for array type, or parameter when allowMultiple=True
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
        """ array primitives should be for 'path', 'header', 'query'.
        Therefore, this kind of convertion is reasonable.

        :return: the converted string
        :rtype: str
        """
        s = ''
        for v in self:
            s = ''.join([s, ',' if s else '', str(v)])
        return s


class Model(dict):
    """ for complex type: models
    """

    # access dict like object
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, obj, val):
        """ constructor

        :param obj.Model obj: model object to instruct how to create this model
        :param val: things used to construct this model
        :type val: dict of json string in str or byte
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
        """ equality operater, 
        will skip checking when both value are None or no attribute.

        :param other: another model
        :type other: primitives.Model or dict
        """
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
        """ convert to json string
        
        note: strip None values before sending on the wire
        """
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
    """ for type void
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
    """ for type File
    """
    def __init__(self, _, val):
        """ constructor

        example val:
        {
            # header values used in multipart/form-data according to RFC2388
            'header': {
                'Content-Type': 'text/plain',
                
                # according to RFC2388, available values are '7bit', '8bit', 'binary'
                'Content-Transfer-Encoding': 'binary'
            },
            filename: 'a.txt',
            data: None (or any file-like object)
        }

        :param val: dict containing file info.
        """
        self.header = val.get('header', {})
        self.data = val.get('data', None)
        self.filename = val.get('filename', '')


class PrimJSONEncoder(json.JSONEncoder):
    """ json encoder for primitives
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
    """ factory function to create primitives

    :param DataTypeObj obj: spec to construct primitives
    :param v: value to construct primitives
    :param bool multiple: if multiple value is enabled.

    :return: the created primitive
    """
    v = obj.defaultValue if v == None else v
    if v == None:
        return None

    # wrap 'allowmultiple' date with array
    if multiple and obj.type != 'array' and isinstance(v, (tuple, list)):
        return Array(obj, v, unique=False);

    ref = getattr(obj, '$ref')
    if ref:
        return ref._prim_(v)
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

    :param dict obj: object to be checked
    :return: True if this object is a primitive.
    """
    return obj.type in prim_types

