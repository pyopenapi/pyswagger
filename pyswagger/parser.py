from __future__ import absolute_import
from .obj import (
    Scope,
    LoginEndpoint,
    Implicit,
    TokenRequestEndpoint,
    Token,
    AuthorizationCode,
    GrantType,
    Authorization,
    ResponseMessage,
    Parameter,
    Operation,
    Api,
    Property,
    Model,
    Resource,
    Info)


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
        pass
            
    def __exit__(self, exc_type, exc_value, traceback):
        """ update what we get as a reference object,
        and put it back to parent context.
        """
        tmp = self.__backref[0][self.__backref[1]]
        obj = self.__class__.__swagger_ref_object__(self._objs)
        if isinstance(tmp, list):
            tmp.append(obj)
            # TODO: check for uniqueness
        elif isinstance(tmp, dict):
            tmp[self.__backref[2]] = obj
        else:
            self.__backref[0][self.__backref[1]] = obj

    def parse(self, obj=None):
        """
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
                        with ctx_kls(self._objs, key, ) as ctx:
                            ctx.process(item)
                if isinstance(items, dict):
                    # for objects grouped in dict
                    for k, v in items:
                        with ctx_kls(self._objs, key, k, ) as ctx:
                            ctx.process(v)
                else:
                    with ctx_kls(self) as ctx:
                        ctx.process(obj.get(key, None))


class ScopeContext(Context):
    """ Context of Scope Object
    """
    __swagger_ref_object__ = Scope
    __swagger_required__ = ['scope']


class LoginEndpointContext(Context):
    """ Context of LoginEndpoint Object
    """
    __swagger_ref_object__ = LoginEndpoint
    __swagger_required__ = ['url']


class ImplicitContext(Context):
    """ Context of Implicit Object
    """
    __swagger_ref_object__ = Implicit
    __swagger_expect__ = [('loginEndpoint', LoginEndpointContext)]
    __swagger_required__ = ['loginEndpoint']


class TokenRequestEndpointContext(Context):
    """ Context of TokenRequestEndpoint Object
    """
    __swagger_ref_object__ = TokenRequestEndpoint
    __swagger_required__ = ['url']


class TokenEndpointContext(Context):
    """ Context of Token Object
    """
    __swagger_ref_object__ = Token
    __swagger_required__ = ['url']


class AuthorizationCodeContext(Context):
    """ Context of AuthorizationCode Object
    """
    __swagger_ref_object__ = AuthorizationCode
    __swagger_expect__ = [
        ('tokenRequestEndpoint', TokenRequestEndpointContext),
        ('tokenEndpoint', TokenEndpointContext)
    ]
    __swagger_required__ = ['tokenRequestEndpoint', 'tokenEndpoint']


class GrantTypeContext(Context):
    """ Context of GrantType Object
    """
    __swagger_ref_object__ = GrantType
    __swagger_expect__ = [
        ('implicit', ImplicitContext),
        ('authorization_code', AuthorizationCodeContext)
    ]


class AuthorizationContext(Context):
    """ Context of Authorization Object
    """
    __swagger_ref_object__ = Authorization
    __swagger_expect__ = [
        ('scopes', ScopeContext),
        ('grantTypes', GrantTypeContext)
    ]
    __swagger_required__ = ['type']


class ResponseMessageContext(Context):
    """ Context of ResponseMessage Object
    """
    __swagger_ref_object__ = ResponseMessage
    __swagger_required__ = ['code', 'message']

 
class ParameterContext(Context):
    """ Context of Parameter Object
    """
    __swagger_ref_object__ = Parameter 
    __swagger_required__ = ['paramType', 'name']


class OperationContext(Context):
    """ Context of Operation Object
    """
    __swagger_ref_object__ = Operation
    __swagger_expect__ = [
        ('authorizations', AuthorizationContext),
        ('parameters', ParameterContext),
        ('responseMessages', ResponseMessageContext)
    ]
    __swagger_required__ = ['method', 'nickname', 'parameters']


class ApiContext(Context):
    """ Context of Api Object
    """
    __swagger_ref_object__ = Api
    __swagger_expect__ = [('operations', OperationContext)]
    __swagger_required__ = ['path', 'operations']


class PropertyContext(Context):
    """ Context of Property Object
    """
    __swagger_ref_object__ = Property


class ModelContext(Context):
    """ Context of Model Object
    """
    __swagger_ref_object__ = Model
    __swagger_expect__ = [('properties', PropertyContext)]
    __swagger_required__ = ['id', 'properties']


class ResourceContext(Context):
    """ Context of Resource Object
    """
    __swagger_ref_object__ = Resource
    __swagger_expect__ = [
        ('apis', ApiContext),
        ('models', ModelContext),
        ('authorizations', AuthorizationContext)
    ]
    __swagger_required__ = ['swaggerVersion', 'basePath', 'apis']

    def __init__(self, parent, name):
        super(ResourceContext, self).__init__(parent)
        self.__name = name


class InfoContext(Context):
    """ Context of Info Object
    """
    __swagger_ref_object__ = Info


class ResourceListContext(Context):
    """ Context of Resource List Object
    """
    __swagger_expect__ = [('authorizations', AuthorizationContext)]
    __swagger_required__ = ['swaggerVersion', 'apis']

    def __init__(self, parent, getter):
        super(ResourceListContext, self).__init__(parent)
        self.__getter = getter

    def parse(self, obj=None):
        obj, _ = self.__getter.next()
        super(ResourceListContext, self).process(obj)

        # get into resource object
        for obj, name in self.__getter:
            with ResourceContext(self, name) as ctx:
                ctx.process(obj=obj)

