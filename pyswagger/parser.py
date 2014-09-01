from __future__ import absolute_import
from .base import Context, NamedContext
from .obj import (
    Scope,
    LoginEndpoint,
    Implicit,
    TokenRequestEndpoint,
    TokenEndpoint,
    AuthorizationCode,
    GrantType,
    Authorization,
    Authorizations,
    ResponseMessage,
    Parameter,
    Operation,
    Api,
    Property,
    Model,
    Resource,
    Info,
    ResourceList)
import six


class ScopeContext(Context):
    """ Context of Scope Object
    """
    __swagger_ref_object__ = Scope


class AuthorizationsContext(NamedContext):
    """ Context of Authorization's' Object
    
    Do not get confused with Authorization Object,
    this one is used in API Declaration
    """
    __swagger_ref_object__ = Authorizations


class LoginEndpointContext(Context):
    """ Context of LoginEndpoint Object
    """
    __swagger_ref_object__ = LoginEndpoint


class ImplicitContext(Context):
    """ Context of Implicit Object
    """
    __swagger_ref_object__ = Implicit
    __swagger_child__ = [('loginEndpoint', LoginEndpointContext)]


class TokenRequestEndpointContext(Context):
    """ Context of TokenRequestEndpoint Object
    """
    __swagger_ref_object__ = TokenRequestEndpoint


class TokenEndpointContext(Context):
    """ Context of Token Object
    """
    __swagger_ref_object__ = TokenEndpoint


class AuthorizationCodeContext(Context):
    """ Context of AuthorizationCode Object
    """
    __swagger_ref_object__ = AuthorizationCode
    __swagger_child__ = [
        ('tokenRequestEndpoint', TokenRequestEndpointContext),
        ('tokenEndpoint', TokenEndpointContext)
    ]


class GrantTypeContext(Context):
    """ Context of GrantType Object
    """
    __swagger_ref_object__ = GrantType
    __swagger_child__ = [
        ('implicit', ImplicitContext),
        ('authorization_code', AuthorizationCodeContext)
    ]


class AuthorizationContext(NamedContext):
    """ Context of Authorization Object
    """
    __swagger_ref_object__ = Authorization
    __swagger_child__ = [
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
    __swagger_child__ = [
        ('authorizations', AuthorizationsContext),
        ('parameters', ParameterContext),
        ('responseMessages', ResponseMessageContext)
    ]


class ApiContext(Context):
    """ Context of Api Object
    """
    __swagger_ref_object__ = Api
    __swagger_child__ = [('operations', OperationContext)]


class PropertyContext(NamedContext):
    """ Context of Property Object
    """
    __swagger_ref_object__ = Property


class ModelContext(NamedContext):
    """ Context of Model Object
    """
    __swagger_ref_object__ = Model
    __swagger_child__ = [('properties', PropertyContext)]

class ResourceContext(Context):
    """ Context of Resource Object
    """
    __swagger_ref_object__ = Resource
    __swagger_child__ = [
        ('apis', ApiContext),
        ('models', ModelContext)
    ]


class InfoContext(Context):
    """ Context of Info Object
    """
    __swagger_ref_object__ = Info


class ResourceListContext(Context):
    """ Context of Resource List Object
    """
    __swagger_ref_object__ = ResourceList
    __swagger_child__ = [
        ('info', InfoContext),
        ('authorizations', AuthorizationContext)]

    def __init__(self, parent, backref, getter):
        super(ResourceListContext, self).__init__(parent, backref)
        self.__getter = getter

    def parse(self, obj=None):
        obj, _ = six.advance_iterator(self.__getter)
        super(ResourceListContext, self).parse(obj=obj)

        # replace each element in 'apis' with Resource
        self._obj['apis'] = {}
        # get into resource object
        for obj, name in self.__getter:
            # here we assume Resource is always a dict
            self._obj['apis'][name] = {}
            with ResourceContext(self._obj['apis'], name) as ctx:
                ctx.parse(obj=obj)

