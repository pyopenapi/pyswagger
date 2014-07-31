from __future__ import absolute_import


class Context(list):
    """ Base of all Contexts

    __swagger_required__: required fields
    __swagger_child__: list of tuples about nested context
    __swagger_ref_obj__: class of reference object, would be used when
    performing request.
    """

    __swagger_required__ = []
    __swagger_child__ = []

    def __init__(self, parent_obj, backref):
        self._parent_obj = parent_obj
        self._backref = backref
        self.__reset_obj()

    def __enter__(self):
        return self

    def __reset_obj(self):
        """
        """
        self._obj = {}

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

        self.__reset_obj()

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
        if self._obj != None:
            for key in (set(obj.keys()) - set(self._obj.keys())):
                self._obj[key] = obj[key]
        else:
            self._obj = obj


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


class BaseObj(object):
    """ Base implementation of all referencial objects,
    make all properties readonly.

    __swagger_fields__: list of names of fields, we will skip fields not
    in this list.
    """

    def __init__(self, ctx):
        super(BaseObj, self).__init__()

        if not issubclass(type(ctx), Context):
            raise TypeError('should provide args[0] as Context, not: ' + ctx.__class__.__name__)

        # handle required fields
        required = set(ctx.__swagger_required__) & set(self.__swagger_fields__)
        for field in required:
            self.add_field(field, ctx._obj[field])

        # handle not-required fields
        not_required = set(self.__swagger_fields__) - set(ctx.__swagger_required__)
        for field in not_required:
            self.add_field(field, ctx._obj.get(field, None))

    def add_field(self, f, obj):
        """ add a field
        """
        if hasattr(self, f):
            raise AttributeError('This attribute already exists:' + f)

        new_name = '_' + self.__class__.__name__ + '__' + f

        setattr(self, new_name, obj)
        setattr(self.__class__, f, property(lambda self: getattr(self, new_name)))


class Items(BaseObj):
    """ Items Object
    """
    __swagger_fields__ = ['type']

    def __init__(self, ctx):
        super(Items, self).__init__(ctx)

        if hasattr(self, 'ref'):
            raise ValueError('Data Type Field duplicated: ref')

        # almost every data field is not required, we just
        # need to make sure either 'type' or '$ref' is shown.
        local_obj = ctx._obj.get('$ref', None)
        self.add_field('ref', local_obj)


class ItemsContext(Context):
    """ Context of Items Object
    """
    __swagger_ref_object__ = Items
    __swagger_required__ = []


class DataTypeObj(BaseObj):
    """ Data Type Fields
    """
    __swagger_fields__ = [
        'type',
        '$ref',
        'format',
        'defaultValue',
        'enum',
        'items',
        'minimum',
        'maximum',
        'uniqueItems'
    ]

    def __init__(self, ctx):
        super(DataTypeObj, self).__init__(ctx)

        # Items Object, too lazy to create a Context for DataTypeObj
        # to wrap this child.
        with ItemsContext(ctx._obj, 'items') as items_ctx:
            items_ctx.parse(ctx._obj.get('items', None))

        type_fields = set(DataTypeObj.__swagger_fields__) - set(ctx.__swagger_required__)
        for field in type_fields:
            if hasattr(self, field):
                raise ValueError('Data Type Field duplicated: ' + field)

            # almost every data field is not required, we just
            # need to make sure either 'type' or '$ref' is shown.
            local_obj = ctx._obj.get(field, None)

            # '$ref' is an invalid name of python attribute.
            field = 'ref' if field == '$ref' else field

            self.add_field(field, local_obj)

