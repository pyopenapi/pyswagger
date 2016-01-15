from __future__ import absolute_import
from ..base import Context, ContainerType
from .objects import (
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
from ...consts import private
from ...utils import url_dirname, url_join


class ScopeContext(Context):
    """ Context of Scope Object
    """
    __swagger_ref_object__ = Scope


class AuthorizationsContext(Context):
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
    __swagger_child__ = {'loginEndpoint': (None, LoginEndpointContext)}


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
    __swagger_child__ = {
        'tokenRequestEndpoint': (None, TokenRequestEndpointContext),
        'tokenEndpoint': (None, TokenEndpointContext)
    }


class GrantTypeContext(Context):
    """ Context of GrantType Object
    """
    __swagger_ref_object__ = GrantType
    __swagger_child__ = {
        'implicit': (None, ImplicitContext),
        'authorization_code': (None, AuthorizationCodeContext)
    }


class AuthorizationContext(Context):
    """ Context of Authorization Object
    """
    __swagger_ref_object__ = Authorization
    __swagger_child__ = {
        'scopes': (ContainerType.list_, ScopeContext),
        'grantTypes': (None, GrantTypeContext)
    }


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
    __swagger_child__ = {
        'authorizations': (ContainerType.dict_of_list_, AuthorizationsContext),
        'parameters': (ContainerType.list_, ParameterContext),
        'responseMessages': (ContainerType.list_, ResponseMessageContext)
    }


class ApiContext(Context):
    """ Context of Api Object
    """
    __swagger_ref_object__ = Api
    __swagger_child__ = {'operations': (ContainerType.list_, OperationContext)}


class PropertyContext(Context):
    """ Context of Property Object
    """
    __swagger_ref_object__ = Property


class ModelContext(Context):
    """ Context of Model Object
    """
    __swagger_ref_object__ = Model
    __swagger_child__ = {'properties': (ContainerType.dict_, PropertyContext)}

class ResourceContext(Context):
    """ Context of Resource Object
    """
    __swagger_ref_object__ = Resource
    __swagger_child__ = {
        'apis': (ContainerType.list_, ApiContext),
        'models': (ContainerType.dict_, ModelContext)
    }


class InfoContext(Context):
    """ Context of Info Object
    """
    __swagger_ref_object__ = Info


class ResourceListContext(Context):
    """ Context of Resource List Object
    """
    __swagger_ref_object__ = ResourceList
    __swagger_child__ = {
        'info': (None, InfoContext),
        'authorizations': (ContainerType.dict_, AuthorizationContext)
    }

    def __init__(self, parent, backref):
        super(ResourceListContext, self).__init__(parent, backref)

    def parse(self, obj, root_url, resolver, getter):
        super(ResourceListContext, self).parse(obj=obj)

        resources = []
        if private.SCHEMA_APIS in obj:
            if isinstance(obj[private.SCHEMA_APIS], list):
                for api in obj[private.SCHEMA_APIS]:
                    resources.append(api[private.SCHEMA_PATH])
            else:
                raise TypeError('Invalid type of apis: ' + type(obj[private.SCHEMA_APIS]))
        base = url_dirname(root_url)
        urls = zip(
            map(lambda u: url_join(base,  u[1:]), resources),
            map(lambda u: u[1:], resources)
        )

        # replace each element in 'apis' with Resource
        self._obj['apis'] = {}
        # get into resource object
        for url, name in urls:
            # here we assume Resource is always a dict
            self._obj['apis'][name] = {}
            res = resolver.resolve(url, getter)
            with ResourceContext(self._obj['apis'], name) as ctx:
                ctx.parse(obj=res)

