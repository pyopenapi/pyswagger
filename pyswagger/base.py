from __future__ import absolute_import


class Context(list):
    """ Base of all Contexts

    __swagger_required__: required fields
    __swagger_expect__: list of tuples about nested context
    __swagger_ref_obj__: class of reference object, would be used when
    performing request.
    """
    def __init__(self, backref):
        self.__backref = backref
        self._obj = {}

    def __enter__(self):
        return self
            
    def __exit__(self, exc_type, exc_value, traceback):
        """ update what we get as a reference object,
        and put it back to parent context.
        """
        if not self.__backref:
            return

        tmp = self.__backref[0][self.__backref[1]]
        obj = self.__class__.__swagger_ref_object__(self)
        if isinstance(tmp, list):
            tmp.append(obj)
            # TODO: check for uniqueness
        elif isinstance(tmp, dict):
            tmp[self.__backref[2]] = obj
        else:
            self.__backref[0][self.__backref[1]] = obj

    def parse(self, obj=None):
        """ go deeper into objects
        """
        if not (obj and isinstance(obj, dict)):
            return

        if hasattr(self, '__swagger_required__'):
            # check required field
            missing = set(self.__class__.__swagger_required__) - set(obj.keys())
            if len(missing):
                raise ValueError('Required: ' + missing)

        if hasattr(self, '__swagger_expect__'):
            # to nested objects
            for key, ctx_kls in self.__swagger_expect__:
                items = obj.get(key, None)
                if isinstance(items, list):
                    # for objects grouped in list
                    for item in items:
                        with ctx_kls((self._obj, key,)) as ctx:
                            ctx.parse(item)
                if isinstance(items, dict):
                    # for objects grouped in dict
                    for k, v in items.iteritems():
                        with ctx_kls((self._obj, key, k,)) as ctx:
                            ctx.parse(v)
                else:
                    with ctx_kls(self) as ctx:
                        ctx.parse(obj.get(key, None))


class BaseObj(object):
    """ Base implementation of all referencial objects,
    make all properties readonly.

    __swagger_fields__: list of names of fields, we will skip fields not
    in this list.
    __swagger_data_type_fields__: indicate this object contains data type fields
    """

    __swagger_data_type_fields__ = False

    def __init__(self, ctx):
        super(BaseObj, self).__init__()

        if not issubclass(type(ctx), Context):
            raise TypeError('should provide args[0] as Context, not: ' + ctx.__class__.__name__)

        def add_field(f, required=False):
            if f in self:
                raise AttributeError('This attribute already exists:' + f)

            new_name = '__' + f

            if required:
                setattr(self, new_name, ctx._obj[f])
            else:
                setattr(self, new_name, ctx._obj.get(f, None))

            setattr(f, property(lambda self: getattr(self, new_name)))

        # handle required fields
        required = set(ctx.__swagger_required__) & set(self.__swagger_fields__)
        for field in required:
            add_field(field, required=True)

        # handle not-required fields
        not_required = set(self.__swagger_fields__) - set(ctx.__swagger_required__)
        for field in not_required:
            add_field(field)

