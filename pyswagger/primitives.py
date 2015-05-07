from __future__ import absolute_import
from .utils import from_iso8601, deref, CycleGuard
from pyswagger import errs
import datetime
import functools
import six
import base64
import json

# TODO: add type: 'object'

class Byte(object):
    """ for string type, byte format
    """

    def __init__(self, _, v):
        """ constructor

        :param str v: accept six.string_types, six.binary_type
        """
        if isinstance(v, six.binary_type):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = v.encode('utf-8')
        else:
            raise ValueError('Unsupported type for Byte: ' + str(type(v)))

    def __str__(self):
        return self.v.decode('utf-8')

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
        return self.v.isoformat()


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
            self.v = datetime.datetime.utcfromtimestamp(v)
        elif isinstance(v, datetime.datetime):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = from_iso8601(v)
        else:
            raise ValueError('Unrecognized type for Datetime: ' + str(type(v)))


class Array(list):
    """ for array type, or parameter when allowMultiple=True
    """

    def __init__(self):
        """ v: list or string_types
        """
        super(Array, self).__init__()
        self.__collection_format = 'csv'

    def apply_with(self, obj, val, _):
        """
        """
        if isinstance(val, six.string_types):
            val = json.loads(val)

        val = set(val) if obj.uniqueItems else val

        if obj.items and len(val):
            self.extend(map(functools.partial(prim_factory, obj.items), val))
            val = []

        # init array as list
        if obj.minItems and len(self) < obj.minItems:
            raise errs.ValidationError('Array should be more than {0}, not {1}'.format(obj.minItems, len(self)))
        if obj.maxItems and len(self) > obj.maxItems:
            raise errs.ValidationError('Array should be less than {0}, not {1}'.format(obj.maxItems, len(self)))

        self.__collection_format = getattr(obj, 'collectionFormat', 'csv')
        return val

    def __str__(self):
        """ array primitives should be for 'path', 'header', 'query'.
        Therefore, this kind of convertion is reasonable.

        :return: the converted string
        :rtype: str
        """
        def _conv(p):
            s = ''
            for v in self:
                s = ''.join([s, p if s else '', str(v)])
            return s
    
        if self.__collection_format == 'csv':
            return _conv(',')
        elif self.__collection_format == 'ssv':
            return _conv(' ')
        elif self.__collection_format == 'tsv':
            return _conv('\t')
        elif self.__collection_format == 'pipes':
            return _conv('|')
        else:
            raise errs.SchemaError('Unsupported collection format when converting to str: {0}'.format(self.__collection_format))

    def to_url(self):
        """ special function for handling 'multi',
        refer to Swagger 2.0, Parameter Object, collectionFormat
        """
        if self.__collection_format == 'multi':
            return [str(s) for s in self]
        else:
            return [str(self)]


class Model(dict):
    """ for complex type: models
    """

    # access dict like object
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, o):
        """ constructor
        """
        super(Model, self).__init__()

    def apply_with(self, obj, val, ctx):
        """ recursivly apply Schema object

        :param obj.Model obj: model object to instruct how to create this model
        :param val: things used to construct this model
        :type val: dict of json string in str or byte
        """
        if isinstance(val, six.string_types):
            val = json.loads(val)
        elif isinstance(val, six.binary_type):
            # TODO: encoding problem...
            val = json.loads(val.decode('utf-8'))

        for k, v in six.iteritems(val):
            if k in obj.properties:
                pobj = obj.properties.get(k)
                self[k] = prim_factory(pobj, v)

            # TODO: patternProperties here
            # TODO: fix bug, everything would not go into additionalProperties, instead of recursive
            elif obj.additionalProperties == True:
                ctx['addp'] = True
            elif obj.additionalProperties not in (None, False):
                ctx['addp_schema'] = obj

        in_obj = set(six.iterkeys(obj.properties))
        in_self = set(six.iterkeys(self))

        other_prop = in_obj - in_self
        for k in other_prop:
            p = obj.properties[k]
            if p.is_set("default"):
                self[k] = prim_factory(p, p.default)

        not_found = set(obj.required) - set(six.iterkeys(self))
        if len(not_found):
            raise ValueError('requirement not meet: {0}'.format(not_found))

        # remove assigned properties to avoid duplicated
        # primitive creation
        _val = {}
        for k in set(six.iterkeys(val)) - in_obj:
            _val[k] = val[k]

        if obj.discriminator:
            self[obj.discriminator] = ctx['name']

        return _val

    def cleanup(self, val, ctx):
        """
        """
        if ctx['addp'] == True:
            for k, v in six.iteritems(val):
                self[k] = v
            ctx['addp'] = False
        elif ctx['addp_schema'] != None:
            obj = ctx['addp_schema']
            for k, v in six.iteritems(val):
                self[k] = prim_factory(obj.additionalProperties, v)
            ctx['addp_schema'] = None

        return {}

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


def apply_with(ret, obj):
    """ helper function for Number, Integer, String.
    These types didn't have a class, so can't have apply_with
    member function.

    Their apply_with would be implemented here.
    """
    def _comp_(vv, o, is_max):
        n = getattr(o, 'maximum' if is_max else 'minimum', None)
        if n == None:
            return

        _eq = getattr(o, 'exclusiveMaximum' if is_max else 'exclusiveMinimum', False)
        if is_max:
            to_raise = vv >= n if _eq else vv > n
        else:
            to_raise = vv <= n if _eq else vv < n

        if to_raise:
            raise errs.ValidationError('condition failed: {0}, v:{1} compared to o:{2}'.format('maximum' if is_max else 'minimum', vv, n))

    if isinstance(ret, six.integer_types):
        _comp_(ret, obj, False)
        _comp_(ret, obj, True)
    elif isinstance(ret, six.string_types):
        if obj.enum and ret not in obj.enum:
            raise errs.ValidationError('{0} is not a valid enum for {1}'.format(ret, str(obj.enum)))
        if obj.maxLength and len(ret) > obj.maxLength:
            raise errs.ValidationError('[{0}] is longer than {1} characters'.format(ret, str(obj.maxLength)))
        if obj.minLength and len(ret) < obj.minLength:
            raise errs.ValidationError('[{0}] is shoter than {1} characters'.format(ret, str(obj.minLength)))
        # TODO: handle pattern
    elif isinstance(ret, float):
        _comp_(ret, obj, False)
        _comp_(ret, obj, True)
        if obj.multipleOf and ret % obj.multipleOf != 0:
            raise errs.ValidationError('{0} should be multiple of {1}'.format(ret, obj.multipleOf))
    else:
        raise errs.ValidationError('Unknown Type: {0}'.format(type(ret)))


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

def create_bool(_, v):
    return bool(v)

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

    # TODO: add validation for email, uuid
    # TODO: add convertion of uuid from python's one
    ('string', 'email'): create_str,
    ('string', 'uuid'): create_str,

    ('string', 'byte'): Byte,
    ('string', 'date'): Date,
    ('string', 'date-time'): Datetime,

    # bool
    ('boolean', ''): create_bool,
    ('boolean', None): create_bool,

    # file
    ('file', ''): File,
    ('file', None): File,
};


prim_types = [
    'integer',
    'number',
    'string',
    'boolean',
    'file',
    'array',
]


def prim_factory(obj, val, ctx=None):
    """ factory function to create primitives

    :param pyswagger.spec.v2_0.objects.Schema obj: spec to construct primitives
    :param val: value to construct primitives

    :return: the created primitive
    """
    val = obj.default if val == None else val
    if val == None:
        return None

    cleanup = ctx == None # it's the top-most call in recursive
    obj = deref(obj)
    ctx = {} if ctx == None else ctx
    if 'name' not in ctx and hasattr(obj, 'name'):
        ctx['name'] = obj.name
    if 'guard' not in ctx:
        ctx['guard'] = CycleGuard()
    if 'addp_schema' not in ctx:
        ctx['addp_schema'] = None
    if 'addp' not in ctx:
        ctx['addp'] = False

    # cycle guard
    ctx['guard'].update(obj)

    ret = None
    if obj.type:
        if isinstance(obj.type, six.string_types):
            if obj.type == 'array':
                ret = Array()
                val = ret.apply_with(obj, val, ctx)
            else:
                t = prim_obj_map.get((obj.type, obj.format), None)
                if not t:
                    raise ValueError('Can\'t resolve type from:(' + str(obj.type) + ', ' + str(obj.format) + ')')

                ret = t(obj, val)
        else:
            raise errs.SchemaError('obj.type should be str, not {0}'.format(type(o.type)))
    elif len(obj.properties) or obj.additionalProperties:
        ret = Model(obj)
        val = ret.apply_with(obj, val, ctx)

    if isinstance(ret, (Date, Datetime, Byte, File)):
        # it's meanless to handle allOf for these types.
        return ret

    is_member = hasattr(ret, 'apply_with')
    def _apply(r, o, v, c):
        if is_member == True:
            v = r.apply_with(o, v, c)
        else:
            apply_with(r, o)

        return v

    # handle allOf for Schema Object
    allOf = getattr(obj, 'allOf', None)
    if allOf:
        not_applied = []
        for a in allOf:
            a = deref(a)
            if not ret:
                # try to find right type for this primitive.
                ret = prim_factory(a, val, ctx)
                is_member = hasattr(ret, 'apply_with')
            else:
                val = _apply(ret, a, val, ctx)

            if not ret:
                # if we still can't determine the type,
                # keep this Schema object for later use.
                not_applied.append(a)
        if ret:
            for a in not_applied:
                val = _apply(ret, a, val, ctx)

    if ret and cleanup and hasattr(ret, 'cleanup'):
        val = ret.cleanup(val, ctx)

    return ret


def is_primitive(obj):
    """ check if a given object refering to a primitive
    defined in spec.

    :param dict obj: object to be checked
    :return: True if this object is a primitive.
    """
    return obj.type in prim_types

