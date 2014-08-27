from __future__ import absolute_import
from .const import SCOPE_SEPARATOR
import six
import datetime
import re


def scope_compose(scope, name):
    new_scope = scope if scope else name
    if scope and name:
        new_scope = scope + SCOPE_SEPARATOR + name

    return new_scope

def scope_split(scope):
    return scope.split(SCOPE_SEPARATOR) if scope else [None]


class ScopeDict(dict):
    """ ScopeDict
    """
    def __getitem__(self, *keys):
        """ to access an obj with key: 'n!##!m', caller can pass as key:
        - n!##!m
        - n, m
        - m (if no collision is found)
        """
        k = six.moves.reduce(lambda k1, k2: scope_compose(k1, k2), keys[0]) if isinstance(keys[0], tuple) else keys[0]
        try:
            return super(ScopeDict, self).__getitem__(k)
        except KeyError as e:
            kk = keys[0]
            ret = []
            if isinstance(kk, six.string_types) and kk.find(SCOPE_SEPARATOR) == -1:
                for ik in self.keys():
                    if ik.endswith(kk):
                        ret.append(ik)
                if len(ret) == 1:
                    return super(ScopeDict, self).__getitem__(ret[0])

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

def from_iso8601(s):
    """ convert iso8601 string to datetime object.
    refer to http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14
    for details.
    """
    m = _iso8601_fmt.match(s)
    if not m:
        raise ValueError('not a valid iso 8601 format string:[{0}]'.format(s))

    g = m.groupdict()

    def _default_zero(key):
        v = g.get(key)
        return int(v) if v else 0

    year = _default_zero('year')
    month = _default_zero('month')
    day = _default_zero('day')
    hour = _default_zero('hour')
    minute = _default_zero('minute')
    second = _default_zero('second')
    tz_s = g.get('tz')

    if not (year and month and day):
        raise ValueError('missing y-m-d: [{0}]'.format(s))

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
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=tz
    )

def dict_compare(a, b):
    """ make 'None' and 'No such attribute' the same """
    for k, v in six.iteritems(a):
        if v != b.get(k, None):
            return False

    residual = set(b.keys()) - set(a.keys())
    for k in residual:
        if b[k] != None:
            return False

    return True

