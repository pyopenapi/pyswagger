from __future__ import absolute_import
from .const import SCOPE_SEPARATOR
import six


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
        k = reduce(lambda k1, k2: scope_compose(k1, k2), keys[0]) if isinstance(keys[0], tuple) else keys[0]
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

