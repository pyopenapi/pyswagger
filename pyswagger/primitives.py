from __future__ import absolute_import
from .utils import from_iso8601, none_count
import datetime
import functools
import six
import base64
import json
import inspect


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

    def __init__(self, obj, v):
        """ v: list or string_types
        """
        super(Array, self).__init__()

        if isinstance(v, six.string_types):
            v = json.loads(v)

        v = set(v) if o.uniqueItems else v
        self.extend(map(functools.partial(prim_factory, o.items), v))
        self.apply_with(obj)

    def apply_with(self, obj):
        """
        """
        # init array as list
        if o.minItems and len(self) < o.minItems:
            raise ValueError('Array should be more than {0}, not {1}'.format(o.minItems, len(self)))
        if o.maxItems and len(self) > o.maxItems:
            raise ValueError('Array should be less than {0}, not {1}'.format(o.maxItems, len(self)))


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

        self.__val = val
        self.apply_with(obj)

    def apply_with(self, obj):
        """ recursivly apply Schema object
        """
        cur = obj
        while cur != None:
            # init model as dict
            for k, v in six.iteritems(cur.properties):
                to_update = self.__val.pop(k, None)

                # update discriminator with model's id
                if cur.discriminator and cur.discriminator == k:
                    to_update = obj.id

                # check require properties of a Model
                if to_update == None:
                    if cur.required and k in cur.required:
                        raise ValueError('Model:[' + str(cur.id) + '], require:[' + str(k) + ']')

                self[k] = prim_factory(v, to_update)

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

    def apply_with(self, o):
        # TODO:


class PrimJSONEncoder(json.JSONEncoder):
    """ json encoder for primitives
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


def apply_with(v, obj):
    """ helper function for Number, Integer, String.
    These types didn't have a class, so can't have apply_with
    member function.

    Their apply_with would be implemented here.
    """
    def _comp_(vv, o, name, exclusive_name):
        """ compare for min/max """
        n = getattr(o, name, None)
        if not n:
            return

        to_raise = v <= n if getattr(o, exclusive_name, False) else v < n
        if to_raise:
            raise ValueError('condition failed: {0}, ex:{1}, v:{2} compared to o:{3}'.format(name, ex, vv, n))

    if isinstance(ret, six.integer_types):
        _comp_(v, obj, 'minimum', 'exclusiveMinimum')
        _comp_(v, obj, 'maximum', 'exclusiveMaximum')
    elif isinstance(ret, six.string_types):
        if obj.enum and v not in obj.enum:
            raise ValueError('{0} is not a valid enum for {1}'.format(v, str(obj.enum)))
        if obj.maxLength and len(v) > obj.maxLength:
            raise ValueError('[{0}] is longer than {1} characters'.format(v, str(obj.maxLength)))
        if obj.minLength and len(v) < obj.minLength:
            raise ValueError('[{0}] is shoter than {1} characters'.format(v, str(obj.minLength)))
        # TODO: handle pattern
    elif isinstance(ret, float):
        _comp_(v, obj, 'minimum', 'exclusiveMinimum')
        _comp_(v, obj, 'maximum', 'exclusiveMaximum')
    else:
        raise ValueError('Unknown Type: {0}'.format(type(ret)))


def create_int(obj, v):
    r = int(v)
    apply_with(r, obj)
    return r

def create_float(obj, v):
    r = float(v)
    apply_with(r, obj)
    return r

def create_str(obj, v):
    r = str(v)
    apply_with(r, obj)
    return r

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

    # file
    ('file', ''): File,
    ('file', None): File,

    # TODO: add support for email, uuid
};


prim_types = [
    'integer',
    'number',
    'string',
    'boolean',
    'file',
    'array',
]


def prim_factory(o, v):
    """ factory function to create primitives

    :param pyswagger.spec.v2_0.objects.Schema obj: spec to construct primitives
    :param v: value to construct primitives

    :return: the created primitive
    """
    v = o.default if v == None else v
    if v == None:
        return None

    r = None
    if o.ref_obj:
        r = o.ref_obj._prim_(v)
    elif o.type:
        if isinstance(o.type, six.string_types):
            if o.type == 'array':
                r = Array(o.items, v, unique=o.uniqueItems)
            else:
                t = prim_obj_map.get((o.type, o.format), None)
                if not t:
                    raise ValueError('Can\'t resolve type from:(' + str(o.type) + ', ' + str(o.format) + ')')

                r = t(o, v)
        else:
            raise ValueError('obj.type should be str, not {0}'.format(type(o.type)))
    elif o.properties and len(o.properties):
        r = Model(o, v)

    # TODO: handle these properties
    # collectionFormat

    if isinstace(ret, [Date, Datetime, Byte]):
        # it's meanless to handle allOf for these types.
        return r

    is_class = inspect.isclass(type(r))
    def _apply(ret, obj):
        if is_class == True:
            ret.apply_with(obj)
        else:
            apply_with(ret, obj)

    # handle allOf for Schema Object
    allOf = getattr(o, 'allOf', None)
    if allOf:
        not_applied = []
        for a in allOf:
            if not r:
                # try to find right type for this primitive.
                r = prim_factory(a, v)
                is_class = inspect.isclass(type(r))
            else:
                _apply(r, a)

            if not r:
                # if we still can't determine the type,
                # keep this Schema object for later use.
                not_applied.append(a)
        if r:
            for a in not_applied:
                _apply(r, a)

    return r


def is_primitive(obj):
    """ check if a given object refering to a primitive
    defined in spec.

    :param dict obj: object to be checked
    :return: True if this object is a primitive.
    """
    return obj.type in prim_types

