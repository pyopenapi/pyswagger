from __future__ import absolute_import
from .base import Context
from .obj import (
    Scope,
    LoginEndpoint,
    Implicit,
    TokenRequestEndpoint,
    TokenEndpoint,
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
import six


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
    __swagger_ref_object__ = TokenEndpoint
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
    __swagger_required__ = ['title', 'description']


class ResourceListContext(Context):
    """ Context of Resource List Object
    """
    __swagger_expect__ = [('authorizations', AuthorizationContext)]
    __swagger_required__ = ['swaggerVersion', 'apis']

    def __init__(self, parent, getter):
        super(ResourceListContext, self).__init__(None)
        self.__getter = getter

    def parse(self, obj=None):
        obj, _ = six.advance_iterator(self.__getter)
        super(ResourceListContext, self).parse(obj)

        # get into resource object
        for obj, name in self.__getter:
            with ResourceContext(self, name) as ctx:
                ctx.parse(obj=obj)

