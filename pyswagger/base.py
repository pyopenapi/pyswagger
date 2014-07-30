from __future__ import absolute_import


class Context(list):
    """ Base of all Contexts

    __swagger_required__: required fields
    __swagger_child__: list of tuples about nested context
    __swagger_ref_obj__: class of reference object, would be used when
    performing request.
    __swagger_named__: this context is identified by a name and grouped
    in a dict.
    """

    __swagger_required__ = []
    __swagger_child__ = []
    __swagger_named__ = False

    def __init__(self, parent_obj, backref):
        self._parent_obj = parent_obj
        self._backref = backref
        self._obj = {}

    def __enter__(self):
        return self

    def back2parent(self, parent_obj, backref):
        """ update what we get as a reference object,
        and put it back to parent context.
        """
        if not self._obj:
            # TODO: a warning for empty object?
            return

        obj = self.__class__.__swagger_ref_object__(self)
        if isinstance(parent_obj[backref], list):
            parent_obj[backref].append(obj)
            # TODO: check for uniqueness
        else:
            parent_obj[backref] = obj

    def __exit__(self, exc_type, exc_value, traceback):
        return self.back2parent(self._parent_obj, self._backref)

    def parse(self, obj=None):
        """ go deeper into objects
        """
        if not obj:
            return

        if not isinstance(obj, dict):
            raise ValueError('invalid obj passed: ' + str(type(obj)))

        if hasattr(self, '__swagger_required__'):
            # check required field
            missing = set(self.__class__.__swagger_required__) - set(obj.keys())
            if len(missing):
                raise ValueError('Required: ' + str(missing))

        if hasattr(self, '__swagger_child__'):
            # to nested objects
            for key, ctx_kls in self.__swagger_child__:
                items = obj.get(key, None)
                if isinstance(items, list):
                    # for objects grouped in list
                    self._obj[key] = []
                    for item in items:
                        with ctx_kls(self._obj, key) as ctx:
                            ctx.parse(obj=item)
                else:
                    self._obj[key] = {}
                    nested_obj = obj.get(key, None)
                    with ctx_kls(self._obj, key) as ctx:
                        ctx.parse(obj=nested_obj)

        # update _obj with obj
        for key in (set(obj.keys()) - set(self._obj.keys())):
            self._obj[key] = obj[key]


class BaseObj(object):
    """ Base implementation of all referencial objects,
    make all properties readonly.

    __swagger_fields__: list of names of fields, we will skip fields not
    in this list.
    __swagger_data_type_fields__: indicate this object contains data type fields
    """

    __swagger_fields__ = []
    __swagger_data_type_fields__ = False

    def __init__(self, ctx):
        super(BaseObj, self).__init__()

        if not issubclass(type(ctx), Context):
            raise TypeError('should provide args[0] as Context, not: ' + ctx.__class__.__name__)

        def add_field(f, required=False):
            if hasattr(self, f):
                raise AttributeError('This attribute already exists:' + f)

            new_name = '__' + f

            if required:
                setattr(self, new_name, ctx._obj[f])
            else:
                setattr(self, new_name, ctx._obj.get(f, None))

            setattr(self, f, property(lambda self: getattr(self, new_name)))


        # handle required fields
        required = set(ctx.__swagger_required__) & set(self.__swagger_fields__)
        for field in required:
            add_field(field, required=True)

        # handle not-required fields
        not_required = set(self.__swagger_fields__) - set(ctx.__swagger_required__)
        for field in not_required:
            add_field(field)


class NamedContext(Context):
    """ for named object
    """
    def parse(self, obj=None):
        if not isinstance(obj, dict):
            raise ValueError('invalid obj passed: ' + str(type(obj)))

        for k, v in obj.iteritems():
            if isinstance(v, list):
                self._parent_obj[self._backref][k] = []
                for item in v:
                    super(NamedContext, self).parse(item)
                    self.back2parent(self._parent_obj[self._backref], k)
            elif isinstance(v, dict):
                super(NamedContext, self).parse(v)
                self._parent_obj[self._backref][k] = None
                self.back2parent(self._parent_obj[self._backref], k)
            else:
                raise ValueError('Unknown item type: ' + str(type(v)))

