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
    Model,
    Resource,
    Info)


class Context(list):
    """ Base of all Contexts

    __swagger_required__: required fields
    __swagger_expect__: list of tuples about nested context
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
        if isinstance(tmp, list):
            tmp.append(self.__class__.__swagger_ref_object__(self._objs))
            # TODO: check for uniqueness
        elif isinstance(tmp, dict):
            # TODO: key name
            tmp.update(self.__class__.__swagger_ref_object__(self._objs))
        else:
            self.__backref[0][self.__backref[1]] = self.__class__.__swagger_ref_object__(self._objs)

    def process(self, obj=None):
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
                    # for objects that grouped in list
                    for item in items:
                        with ctx_kls(self._objs, key,) as ctx:
                            ctx.process(item)
                else:
                    with ctx_kls(self) as ctx:
                        ctx.process(obj.get(key, None))


class ScopeContext(Context):
    """ Context of Scope Object
    """
    __swagger_ref_object__ = Scope


class LoginEndpointContext(Context):
    """ Context of LoginEndpoint Object
    """
    __swagger_ref_object__ = LoginEndpoint


class ImplicitContext(Context):
    """ Context of Implicit Object
    """
    __swagger_ref_object__ = Implicit
    __swagger_expect__ = [('loginEndpoint', LoginEndpointContext)]


class TokenRequestEndpointContext(Context):
    """ Context of TokenRequestEndpoint Object
    """
    __swagger_ref_object__ = TokenRequestEndpoint


class TokenEndpoint(Context):
    """ Context of Token Object
    """
    __swagger_ref_object__ = Token


class AuthorizationCodeContext(Context):
    """ Context of AuthorizationCode Object
    """
    __swagger_ref_object__ = AuthorizationCode
    __swagger_expect__ = [
        ('tokenRequestEndpoint', TokenRequestEndpointContext),
        ('tokenEndpoint', TokenEndpoint)
    ]


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


class ResponseMessageContext(Context):
    """ Context of ResponseMessage Object
    """
    __swagger_ref_object__ = ResponseMessage

 
class ParameterContext(Context):
    """ Context of Parameter Object
    """
    __swagger_ref_object__ = Parameter 


class OperationContext(Context):
    """ Context of Operation Object
    """
    __swagger_ref_object__ = Operation
    __swagger_expect__ = [
        ('authorizations', AuthorizationContext),
        ('parameters', ParameterContext),
        ('responseMessages', ResponseMessageContext)
    ]


class ApiContext(Context):
    """ Context of Api Object
    """
    __swagger_ref_object__ = Api
    __swagger_expect__ = [('operations', OperationContext)]


class ModelContext(Context):
    """ Context of Model Object
    """
    __swagger_ref_object__ = Model


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

    def process(self, obj=None):
        obj, _ = self.__getter.next()
        super(ResourceListContext, self).process(obj)

        # get into resource object
        for obj, name in self.__getter:
            with ResourceContext(self, name) as ctx:
                ctx.process(obj=obj)

