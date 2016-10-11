from __future__ import absolute_import
from .consts import private
from .errs import CycleDetectionError
import six
import imp
import sys
import datetime
import re
import os
import operator
import functools

#TODO: accept varg
def scope_compose(scope, name, sep=private.SCOPE_SEPARATOR):
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

def scope_split(scope, sep=private.SCOPE_SEPARATOR):
    """ split a scope into names
    
    :param str scope: scope to be splitted
    :return: list of str for scope names
    """

    return scope.split(sep) if scope else [None]


class ScopeDict(dict):
    """ ScopeDict
    """
    def __init__(self, *a, **k):
        self.__sep = private.SCOPE_SEPARATOR
        super(ScopeDict, self).__init__(*a, **k)

    @property
    def sep(self):
        """ separator property
        """
        raise TypeError('sep property is write-only')

    @sep.setter
    def sep(self, sep):
        """ update separater used here
        """
        self.__sep = sep

    def __getitem__(self, *keys):
        """ to access an obj with key: 'n!##!m...!##!z', caller can pass as key:
        - n!##!m...!##!z
        - n, m, ..., z
        - z
        when separater == !##!

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


class CycleGuard(object):
    """ Guard for cycle detection
    """

    def __init__(self):
        self.__visited = []

    def update(self, obj):
        if obj in self.__visited:
            raise CycleDetectionError('Cycle detected: {0}'.format(getattr(obj, '$ref', None)))
        self.__visited.append(obj)


# TODO: this function and datetime don't handle leap-second.
#       check if dateutil handle it or not

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
    '(?P<hour>\d{2}):(?P<minute>\d{2})(:(?P<second>\d{1,2})(\.(?P<microsecond>\d{1,6}))?)?', # hh:mm:ss.ms
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
    microsecond = g.get('microsecond', None)
    if microsecond is not None:
        # append zero when not matching 6 digits
        microsecond = int(microsecond + '0' * (6 - len(microsecond)))
    tz_s = g.get('tz')

    if not (year and month and day):
        raise ValueError('missing y-m-d: [{0}]'.format(s))

    # only date part, time part is none
    if hour == None and minute == None and second == None:
        return datetime.datetime(year, month, day)

    # prepare tz info
    tz = None
    if tz_s:
        if hour is None and minute is None:
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
        microsecond=microsecond or 0,
        tzinfo=tz
    )

def import_string(name):
    """ import module
    """
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

def jr_split(s):
    """ split a json-reference into (url, json-pointer)
    """
    p = six.moves.urllib.parse.urlparse(s)
    return (
        normalize_url(six.moves.urllib.parse.urlunparse(p[:5]+('',))),
        '#'+p.fragment if p.fragment else '#'
    )

def deref(obj, guard=None):
    """ dereference $ref
    """
    cur, guard = obj, guard or CycleGuard()
    guard.update(cur)
    while cur and getattr(cur, 'ref_obj', None) != None:
        cur = cur.ref_obj
        guard.update(cur)
    return cur

def final(obj):
    return obj.final if getattr(obj, 'final', None) else obj

def get_dict_as_tuple(d):
    """ get the first item in dict,
    and return it as tuple.
    """
    for k, v in six.iteritems(d):
        return k, v
    return None

def nv_tuple_list_replace(l, v):
    """ replace a tuple in a tuple list
    """
    _found = False
    for i, x in enumerate(l):
        if x[0] == v[0]:
            l[i] = v
            _found = True

    if not _found:
        l.append(v)

def path2url(p):
    """ Return file:// URL from a filename.
    """
    return six.moves.urllib.parse.urljoin(
        'file:', six.moves.urllib.request.pathname2url(p)
    )

def normalize_url(url):
    """ Normalize url
    """
    if not url:
        return url

    p = six.moves.urllib.parse.urlparse(url)
    if p.scheme == '':
        if p.netloc == '' and p.path != '':
            # it should be a file path
            url = path2url(os.path.abspath(url))
        else:
            raise ValueError('url should be a http-url or file path -- ' + url)

    return url

def url_dirname(url):
    """ Return the folder containing the '.json' file
    """
    p = six.moves.urllib.parse.urlparse(url)
    for e in [private.FILE_EXT_JSON, private.FILE_EXT_YAML]:
        if p.path.endswith(e):
            return six.moves.urllib.parse.urlunparse(
                p[:2]+
                (os.path.dirname(p.path),)+
                p[3:]
            )
    return url

def url_join(url, path):
    """ url version of os.path.join
    """
    p = six.moves.urllib.parse.urlparse(url)
    return six.moves.urllib.parse.urlunparse(
        p[:2]+
        (os.path.join(p.path, path),)+
        p[3:]
    )

def normalize_jr(jr, url=None):
    """ normalize JSON reference, also fix
    implicit reference of JSON pointer.
    input:
    - #/definitions/User
    - http://test.com/swagger.json#/definitions/User
    output:
    - http://test.com/swagger.json#/definitions/User

    input:
    - some_folder/User.json
    output:
    - http://test.com/some_folder/User.json
    """

    if jr == None:
        return jr

    idx = jr.find('#')
    path, jp = (jr[:idx], jr[idx+1:]) if idx != -1 else (jr, None)

    if len(path) > 0:
        p = six.moves.urllib.parse.urlparse(path)
        if p.scheme == '' and url:
            p = six.moves.urllib.parse.urlparse(url)
            # it's the path of relative file
            path = six.moves.urllib.parse.urlunparse(p[:2]+(os.path.join(os.path.dirname(p.path), path),)+p[3:])
    else:
        path = url

    if path:
        return ''.join([path, '#', jp]) if jp else path
    else:
        return '#' + jp

def is_file_url(url):
    return url.startswith('file://')

def get_swagger_version(obj):
    """ get swagger version from loaded json """

    if isinstance(obj, dict):
        if 'swaggerVersion' in obj:
            return obj['swaggerVersion']
        elif 'swagger' in obj:
            return obj['swagger']
        return None
    else:
        # should be an instance of BaseObj
        return obj.swaggerVersion if hasattr(obj, 'swaggerVersion') else obj.swagger

def walk(start, ofn, cyc=None):
    """ Non recursive DFS to detect cycles

    :param start: start vertex in graph
    :param ofn: function to get the list of outgoing edges of a vertex
    :param cyc: list of existing cycles, cycles are represented in a list started with minimum vertex.
    :return: cycles
    :rtype: list of lists
    """
    ctx, stk = {}, [start]
    cyc = [] if cyc == None else cyc

    while len(stk):
        top = stk[-1]

        if top not in ctx:
            ctx.update({top:list(ofn(top))})

        if len(ctx[top]):
            n = ctx[top][0]
            if n in stk:
                # cycles found,
                # normalize the representation of cycles,
                # start from the smallest vertex, ex.
                # 4 -> 5 -> 2 -> 7 -> 9 would produce
                # (2, 7, 9, 4, 5)
                nc = stk[stk.index(n):]
                ni = nc.index(min(nc))
                nc = nc[ni:] + nc[:ni] + [min(nc)]
                if nc not in cyc:
                    cyc.append(nc)

                ctx[top].pop(0)
            else:
                stk.append(n)
        else:
            ctx.pop(top)
            stk.pop()
            if len(stk):
                ctx[stk[-1]].remove(top)

    return cyc

def _diff_(src, dst, ret=None, jp=None, exclude=[], include=[]):
    """ compare 2 dict/list, return a list containing
    json-pointer indicating what's different, and what's diff exactly.

    - list length diff: (jp, length of src, length of dst)
    - dict key diff: (jp, None, None)
    - when src is dict or list, and dst is not: (jp, type(src), type(dst))
    - other: (jp, src, dst)
    """

    def _dict_(src, dst, ret, jp):
        ss, sd = set(src.keys()), set(dst.keys())
        # what's include is prior to what's exclude
        si, se = set(include or []), set(exclude or [])
        ss, sd = (ss & si, sd & si) if si else (ss, sd)
        ss, sd = (ss - se, sd - se) if se else (ss, sd)

        # added keys
        for k in sd - ss:
            ret.append((jp_compose(k, base=jp), None, None,))

        # removed keys
        for k in ss - sd:
            ret.append((jp_compose(k, base=jp), None, None,))

        # same key
        for k in ss & sd:
            _diff_(src[k], dst[k], ret, jp_compose(k, base=jp), exclude, include)

    def _list_(src, dst, ret, jp):
        if len(src) < len(dst):
            ret.append((jp, len(src), len(dst),))
        elif len(src) > len(dst):
            ret.append((jp, len(src), len(dst),))
        else:
            if len(src) == 0:
                return

            # make sure every element in list is the same
            def r(x, y):
                if type(y) != type(x):
                    raise ValueError('different type: {0}, {1}'.format(type(y).__name__, type(x).__name__))
                return x
            ts = type(functools.reduce(r, src))
            td = type(functools.reduce(r, dst))

            # when type is different
            while True:
                if issubclass(ts, six.string_types) and issubclass(td, six.string_types):
                    break
                if issubclass(ts, six.integer_types) and issubclass(td, six.integer_types):
                    break
                if ts == td:
                    break
                ret.append((jp, str(ts), str(td),))
                return

            if ts != dict:
                ss, sd = sorted(src), sorted(dst)
            else:
                # process dict without sorting
                # TODO: find a way to sort list of dict, (ooch)
                ss, sd = src, dst

            for idx, (s, d) in enumerate(zip(src, dst)):
                _diff_(s, d, ret, jp_compose(str(idx), base=jp), exclude, include)

    ret = [] if ret == None else ret
    jp = '' if jp == None else jp

    if isinstance(src, dict):
        if not isinstance(dst, dict):
            ret.append((jp, type(src).__name__, type(dst).__name__,))
        else:
            _dict_(src, dst, ret, jp)
    elif isinstance(src, list):
        if not isinstance(dst, list):
            ret.append((jp, type(src).__name__, type(dst).__name__,))
        else:
            _list_(src, dst, ret, jp)
    elif src != dst:
        ret.append((jp, src, dst,))

    return ret

def get_or_none(obj, *a):
    ret = obj
    for v in a:
        ret = getattr(ret, v, None)
        if not ret:
            break
    return ret

def patch_path(base_path, path):
    # try to get extension from base_path
    _, ext = os.path.splitext(base_path)
    if ext not in private.VALID_FILE_EXT:
        ext = ''

    # try to get extension from path
    _, ext = os.path.splitext(path) if ext == '' else (None, ext)
    if ext not in private.VALID_FILE_EXT:
        ext = ''

    # .json is default extension to try
    ext = '.json' if ext == '' else ext
    # make sure we get .json or .yaml files
    if not path.endswith(ext):
        path = path + ext

    # trim the leading slash, which is invalid on Windows
    if os.name == 'nt' and path.startswith('/'):
        path = path[1:]

    return path

