from __future__ import absolute_import
from ..spec.v2_0.objects import Parameter, Operation, Schema
from ..utils import deref
import random
import six
import sys
import string
import uuid
import base64
import datetime
import time

# TODO: patternProperties
# TODO: pattern
# TODO: maxProperties, minProperties
# TODO: enum
# TODO: binary

# min/max of integer
maxInt32 = 1 << 31 - 1
minInt32 = -maxInt32
maxInt64 = 1 << 63 - 1
minInt64 = -maxInt64

def _int_(obj, _):
    max_ = maxInt32 if getattr(obj, 'format') in ['int32', None] else maxInt64
    max_ = obj.maximum if obj.maximum else max_
    max_ = max_-1 if obj.exclusiveMaximum else max_

    min_ = minInt32 if getattr(obj, 'format') in ['int32', None] else minInt64
    min_ = obj.minimum if obj.minimum else min_
    min_ = min_+1 if obj.exclusiveMinimum else min_

    out = random.randint(min_, max_)
    return out - (out % obj.multipleOf) if isinstance(obj.multipleOf, six.integer_types) and obj.multipleOf != 0 else out

def _float_(obj, _):
    # TODO: exclusiveMaximum == False is not implemented.
    max_ = obj.maximum if obj.maximum else sys.float_info.max
    min_ = obj.minimum if obj.minimum else sys.float_info.min

    out = None
    while out == None:
        out = min_ + (max_ - min_) * random.random()
        if obj.multipleOf and obj.multipleOf != 0:
            out = int(out / obj.multipleOf) * obj.multipleOf 
        if obj <= min_ and obj.exclusiveMinimum:
            out = None
    return float(out)

def _str_(obj, opt):
    # note: length is 0~100, characters are limited to ASCII
    return ''.join([random.choice(string.ascii_letters) for _ in range(random.randint(0, opt['max_str_length']))])

def _bool_(obj, _):
    return random.randint(0, 1) == 0

def _uuid_(obj, _):
    return uuid.uuid4()

names = list(string.letters) + ['_', '-'] + list(string.digits)
def _email_name_():
    return random.choice(string.letters) \
    + ''.join([random.choice(names) for _ in xrange(random.randint(1, 30))]) \
    + random.choice(string.letters)

def _email_(obj, _):
    host_length = random.randint(2, 100)
    region_length = random.randint(2, 30)
    return '.'.join([_email_name_() for _ in xrange(random.randint(1, 4))]) \
        + '@' \
        + random.choice(string.letters) \
        + ''.join([random.choice(names) for _ in xrange(host_length)]) \
        + '.' \
        + random.choice(string.letters) \
        + ''.join([random.choice(names) for _ in xrange(region_length)])

def _byte_(obj, opt):
    return base64.b64encode( 
        ''.join([random.choice(string.ascii_letters) for _ in range(random.randint(0, opt['max_byte_length']))])
    )

max_date = time.mktime(datetime.date.max.timetuple())
min_date = time.mktime(datetime.date.min.timetuple())
def _date_(obj, _):
    return datetime.date.fromtimestamp(
        random.uniform(min_date, max_date)
    )

max_datetime = time.mktime(datetime.datetime.max.utctimetuple())
min_datetime = time.mktime(datetime.datetime.min.utctimetuple())
def _date_time_(obj, _):
    return datetime.datetime.utcfromtimestamp(
        random.uniform(min_datetime, max_datetime)
    )

class Renderer(object):
    """
    """

    def __init__(self):
        """
        """
        random.seed()

        # init map of generators
        self._map = {
            # int
            'integer': {
                'int32': _int_,
                'int64': _int_,
            },

            # float
            'number': {
                'float': _float_,
                'double': _float_,
            },

            # string
            'string': {
                '': _str_,
                None: _str_,
                'password': _str_,
                'byte': _byte_,
                'date': _date_,
                'date-time': _date_time_,
                'uuid': _uuid_,
                'email': _email_,
            },

            # bool
            'boolean': {
                '': _bool_,
                None: _bool_,
            },

            # TODO: file
        }

    def _get(self, _type, _format=None):
        r = self._map.get(_type, None)
        return None if r == None else r.get(_format, None)

    def _generate(self, obj, opt):
        obj = deref(obj).final
        type_ = getattr(obj, 'type', None)
        out = None
        if type_ == 'object':
            out = {}
            max_ = obj.maxProperties if obj.maxProperties else opt['max_prop_count']
            min_ = obj.minProperties if obj.minProperties else None
            count = 0
            for name, prop in six.iteritems(obj.properties or {}):
                if not name in obj.required:
                    if random.randint(0, 1) == 0 or opt['minimal']:
                        continue
                out[name] = self._generate(prop, opt)
                count = count + 1

            if isinstance(obj.additionalProperties, Schema):
                # TODO: additionalProperties == True is not handled

                # generate random properties
                more = random.randint(min_, max_+1) - count
                if more > 0:
                    # generate a random string as property-name
                    for _ in xrange(more):
                        while True:
                            length = random.randint(0, opt['max_name_length'])
                            name = ''.join([random.choice(string.ascii_letters) for _ in xrange(length)])
                            if name not in out:
                                out[name] = self._generate(obj.additionalProperties, opt)
                                break

        elif type_ == 'array':
            min_ = obj.minItems if obj.minItems else 0
            max_ = obj.maxItems if obj.maxItems else opt['max_array_length']
            out = []
            for _ in xrange(random.randint(min_, max_)):
                out.append(self._generate(obj.items, opt))

        elif type_ != None:
            g = self._get(getattr(obj, 'type', None), getattr(obj, 'format', None))
            if not g:
                raise Exception('Unable to locate generator: {0}'.format(obj))
            out = g(obj, opt)
        else:
            raise Exception('No type info available:{0}, {1}'.format(obj.type, obj.format))

        return out

    @staticmethod
    def default():
        return dict(
            max_depth=10,
            max_name_length=64,
            max_prop_count=32,
            max_str_length=100,
            max_byte_length=100,
            max_array_length=100,
            minimal=False,
        ) 

    def render(self, param, opt=None):
        """
        """
        opt = self.default() if opt == None else opt
        if not isinstance(opt, dict):
            raise ValueError('Not a dict: {0}'.format(opt))

        if isinstance(param, Parameter):
            if getattr(param, 'in', None) == 'body':
                return self._generate(param.schema, opt)
            return self._generate(param, opt)
        elif isinstance(param, Schema):
            return self._generate(param, opt)
        else:
            raise ValueError('Not a Schema/Parameter: {0}'.format(param))

    def render_all(self, params, include=None, exclude=[], opt=None):
        """
        """
        if not instance(params, Operation):
            raise ValueError('Not a Operation: {0}'.format(params))
        if not isinstance(include, list) or not isinstance(exclude, list):
            raise ValueError('Not a list: {0},{1}'.format(include, exclude))
        if not isinstance(opt, dict):
            raise ValueError('Not a dict: {0}'.format(opt))
