from __future__ import absolute_import
from .base import BaseObj
from .utils import scope_compose
import six


def default_tree_traversal(app):
    """ default tree traversal """
    objs = [(None, None, app.schema)]
    while len(objs) > 0:
        scope, name, obj = objs.pop()

        # get children
        new_scope = scope_compose(scope, name)
        objs.extend(map(lambda c: (new_scope,) + c, obj._children_))

        yield scope, name, obj


class DispatcherMeta(type):
    """ metaclass for Dispatcher
    """
    def __new__(metacls, name, bases, spc):
        if 'obj_route' not in spc.keys():
            # forcely create a new obj_route
            # but not share the same one with parents.
            spc['obj_route'] = {}
            spc['result_fn'] = [None]

        return type.__new__(metacls, name, bases, spc)


class Dispatcher(six.with_metaclass(DispatcherMeta, object)):
    """ Dispatcher
    """
    obj_route = {}
    result_fn = [None]

    @classmethod
    def __add_route(cls, t, f):
        """
        """
        if not issubclass(t, BaseObj):
            raise ValueError('target_cls should be a subclass of BaseObj, but got:' + str(t))

        # allow register multiple handler function
        # against one object
        if t in cls.obj_route.keys():
            cls.obj_route[t].append(f)
        else:
            cls.obj_route[t] = [f]

    @classmethod
    def register(cls, target):
        """
        """
        def outer_fn(f):
            # what we did is simple,
            # register target_cls as key, and f as callback
            # then keep this record in cls.
            for t in target:
                cls.__add_route(t, f)

            # nothing is decorated. Just return original one.
            return f

        return outer_fn

    @classmethod
    def result(cls, f):
        """
        """

        # avoid bound error
        cls.result_fn = [f]
        return f


class Scanner(object):
    """ Scanner
    """
    def __init__(self, app):
        super(Scanner, self).__init__()
        self.__app = app

    @property
    def app(self):
        return self.__app

    def __build_route(self, route):
        """
        """
        ret = []
        for r in route:
            for attr in r.__class__.__dict__:
                o = getattr(r, attr)
                if type(o) == DispatcherMeta:
                    ret.append((r, o.obj_route, o.result_fn[0]))

        return ret

    def scan(self, route, nexter=default_tree_traversal):
        """
        """
        merged_r = self.__build_route(route)
        for scope, name, obj in nexter(self.app):
            for the_self, r, res in merged_r:

                def handle_cls(cls):
                    f = r.get(cls, None)
                    if f:
                        for ff in f:
                            res(the_self, ff(the_self, scope, name, obj, self.app)) if res else ff(the_self, scope, name, obj, self.app)

                for cls in obj.__class__.__mro__[:-1]:
                    if cls is BaseObj:
                        break
                    handle_cls(cls)

