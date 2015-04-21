from __future__ import absolute_import
from .spec.base import BaseObj
import six


def default_tree_traversal(root, leaves):
    """ default tree traversal """
    objs = [('#', root)]
    while len(objs) > 0:
        path, obj = objs.pop()

        # name of child are json-pointer encoded, we don't have
        # to encode it again.
        if obj.__class__ not in leaves:
            objs.extend(map(lambda i: (path + '/' + i[0],) + (i[1],), six.iteritems(obj._children_)))

        # the path we expose here follows JsonPointer described here
        #   http://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-07
        yield path, obj


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

    def scan(self, route, root, nexter=default_tree_traversal, leaves=[]):
        """
        """
        if root == None:
            raise ValueError('Can\'t scan because root==None')

        merged_r = self.__build_route(route)
        for path, obj in nexter(root, leaves):
            for the_self, r, res in merged_r:

                def handle_cls(cls):
                    f = r.get(cls, None)
                    if f:
                        for ff in f:
                            ret = ff(the_self, path, obj, self.app)
                            if res:
                                res(the_self, ret)

                for cls in obj.__class__.__mro__[:-1]:
                    if cls is BaseObj:
                        break
                    handle_cls(cls)

