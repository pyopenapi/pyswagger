from __future__ import absolute_import
from .const import SCOPE_SEPARATOR
import six
import imp
import sys
import datetime
import re

#TODO: accept varg
def scope_compose(scope, name, sep=SCOPE_SEPARATOR):
    """ compose a new scope

    :param str scope: current scope
    :param str name: name of next level in scope
    :return the composed scope
    """

    if name == None:
        new_scope = scope
    else:
        new_scope = scope if scope else name

    if scope and name:
        new_scope = scope + sep + name

    return new_scope

def scope_split(scope, sep=SCOPE_SEPARATOR):
    """ split a scope into names
    
    :param str scope: scope to be splitted
    :return: list of str for scope names
    """

    return scope.split(sep) if scope else [None]


class ScopeDict(dict):
    """ ScopeDict
    """
    def __init__(self, *a, **k):
        self.__sep = SCOPE_SEPARATOR
        super(ScopeDict, self).__init__(*a, **k)

    @property
    def sep(self):
        """ separator property
        """
        raise TypeError('sep property is write-only')

    @sep.setter
    def  sep(self, sep):
        self.__sep = sep

    def __getitem__(self, *keys):
        """ to access an obj with key: 'n!##!m...!##!z', caller can pass as key:
        - n!##!m...!##!z
        - n, m, ..., z
        - z

        :param dict keys: keys to access via scopes.
        """
        k = six.moves.reduce(lambda k1, k2: scope_compose(k1, k2, sep=self.__sep), keys[0]) if isinstance(keys[0], tuple) else keys[0]
        try:
            return super(ScopeDict, self).__getitem__(k)
        except KeyError as e:
            ret = []
            for ik in self.keys():
                if ik.endswith(k):
                    ret.append(ik)
            if len(ret) == 1:
                return super(ScopeDict, self).__getitem__(ret[0])
            elif len(ret) > 1:
                raise ValueError('Multiple occurrence of key: {0}'.format(k))

            raise e


class FixedTZ(datetime.tzinfo):
    """ tzinfo implementation without consideration of
    daylight-saving-time.
    """

    def __init__(self, h=0, m=0):
        self.__offset = datetime.timedelta(hours=h, minutes=m)

    def utcoffset(self, dt):
        return self.__offset + self.dst(dt)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

_iso8601_fmt = re.compile(''.join([
    '(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', # YYYY-MM-DD
    'T', # T
    '(?P<hour>\d{2}):(?P<minute>\d{2})(:(?P<second>\d{1,2}))?', # hh:mm:ss
    '(?P<tz>Z|[+-]\d{2}:\d{2})?' # Z or +/-hh:mm
]))
_iso8601_fmt_date = re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})') # YYYY-MM-DD

def from_iso8601(s):
    """ convert iso8601 string to datetime object.
    refer to http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14
    for details.

    :param str s: time in ISO-8601
    :rtype: datetime.datetime
    """
    m = _iso8601_fmt.match(s)
    if not m:
        m = _iso8601_fmt_date.match(s)

    if not m:
        raise ValueError('not a valid iso 8601 format string:[{0}]'.format(s))

    g = m.groupdict()

    def _default_zero(key):
        v = g.get(key, None)
        return int(v) if v else 0

    def _default_none(key):
        v = g.get(key, None)
        return int(v) if v else None

    year = _default_zero('year')
    month = _default_zero('month')
    day = _default_zero('day')
    hour = _default_none('hour')
    minute = _default_none('minute')
    second = _default_none('second')
    tz_s = g.get('tz')

    if not (year and month and day):
        raise ValueError('missing y-m-d: [{0}]'.format(s))

    # only date part, time part is none
    if hour == None and minute == None and second == None:
        return datetime.datetime(year, month, day)

    # prepare tz info
    tz = None
    if tz_s:
        if not (hour and minute):
            raise ValueError('missing h:m when tzinfo is provided: [{0}]'.format(s))

        negtive = hh = mm = 0

        if tz_s != 'Z':
            negtive = -1 if tz_s[0] == '-' else 1
            hh = int(tz_s[1:3])
            mm = int(tz_s[4:6]) if len(tz_s) > 5 else 0

        tz = FixedTZ(h=hh*negtive, m=mm*negtive)

    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour or 0,
        minute=minute or 0,
        second=second or 0,
        tzinfo=tz
    )

def none_count(d):
    """ count none value in dict """
    return six.moves.reduce(lambda x, y: x + 1 if y == None else x, d.values(), 0)

def import_string(name):
    """ import module
    """
    # TODO: unittest
    mod = fp = None

    # code below, please refer to 
    #   https://docs.python.org/2/library/imp.html
    # for details
    try:
        return sys.modules[name]
    except KeyError:
        pass

    try:
        fp, pathname, desc = imp.find_module(name)
        mod = imp.load_module(name, fp, pathname, desc)
    except ImportError:
        mod = None 
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

    return mod

def jp_compose(s, base=None):
    """ append/encode a string to json-pointer
    """
    if s == None:
        return base

    ss = [s] if isinstance(s, six.string_types) else s
    ss = [s.replace('~', '~0').replace('/', '~1') for s in ss]
    if base:
        ss.insert(0, base)
    return '/'.join(ss)

def jp_split(s):
    """ split/decode a string from json-pointer
    """
    if s == '' or s == None:
        return []

    def _decode(s):
        s = s.replace('~1', '/')
        return s.replace('~0', '~')

    return [_decode(ss) for ss in s.split('/')]

def deref(obj):
    o = getattr(obj, 'ref_obj', None) if obj else None
    return o if o else obj

def get_dict_as_tuple(d):
    """ get the first item in dict,
    and return it as tuple.
    """
    # TODO: test case
    for k, v in six.iteritems(d):
        return k, v
    return None

def nv_tuple_list_replace(l, v):
    """ replace a tuple in a tuple list
    """
    # TODO: test case
    _found = False
    for i, x in enumerate(l):
        if x[0] == v[0]:
            l[i] = v
            _found = True

    if not _found:
        l.append(v)

