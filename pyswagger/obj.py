from __future__ import absolute_import
from .base import BaseObj


class Scope(BaseObj):
    """ Scope Object
    """
    __swagger_fields__ = ['scope']

    def __init__(self, ctx):
        super(Scope, self).__init__(ctx)

        self.__scope = kwargs['scope']

    @property
    def scope(self):
        return self.__scope


class LoginEndpoint(BaseObj):
    """ LoginEndpoint Object
    """

    __swagger_fields__ = ['url']

    def __init__(self, ctx):
        super(LoginEndpoint, self).__init__(ctx)

        self.__url = kwargs['url']

    @property
    def url(self):
        return self.__url


class Implicit(BaseObj):
    """ Implicit Object
    """

    __swagger_fields__ = ['loginEndpoint', 'tokenName']

    def __init__(self, ctx):
        super(Implicit, self).__init__(ctx)

        self.__tokenName = kwargs['tokenName']
        self.__loginEndpoint = kwargs['loginEndpoint']

    @property
    def tokenName(self):
        return self.__tokenName

    @property
    def loginEndpoint(self):
        return self.__loginEndpoint


class TokenRequestEndpoint(BaseObj):
    """ TokenRequestEndpoint Object
    """

    __swagger_fields__ = ['url', 'clientIdName', 'clientSecretName']

    def __init__(self, ctx):
        super(TokenRequestEndpoint, self).__init__(ctx)

        self.__url = kwargs['url']
        self.__clientIdName = None
        self.__clientSecretName = None

        if 'clientIdName' in kwargs:
            self.__clientIdName = kwargs['clientIdName']

        if 'clientSecretName' in kwargs:
            self.__clientSecretName = kwargs['clientSecretName']


class TokenEndpoint(BaseObj):
    """ TokenEndpoint Object
    """

    __swagger_fields__ = ['url', 'tokenName']

    def __init__(self, ctx):
        super(TokenEndpoint, self).__init__(ctx)


class AuthorizationCode(BaseObj):
    """ AuthorizationCode Object
    """

    __swagger_fields__ = ['tokenRequestEndpoint', 'tokenEndpoint']

    def __init__(self, ctx):
        super(AuthorizationCode, self).__init__(ctx)


class GrantType(BaseObj):
    """ GrantType Object
    """

    __swagger_fields__ = ['implicit', 'authorization_code']

    def __init__(self, ctx):
        super(GrantType, self).__init__(ctx)


class Authorization(BaseObj):
    """ Authorization Object
    """

    __swagger_fields__ = ['type', 'passAs', 'keyname', 'scopes', 'grantTypes']

    def __init__(self, ctx):
        super(Authorization, self).__init__(ctx)


class ResponseMessage(BaseObj):
    """ ResponseMessage Object
    """

    __swagger_fields__ = ['code', 'message', 'responseModel']

    def __init__(self, ctx):
        super(ResponseMessage, self).__init__(ctx)


class Parameter(BaseObj):
    """ Parameter Object
    """

    __swagger_fields__ = ['paramType', 'name', 'required', 'allowMultiple']
    __swagger_data_type_fields__ = True

    def __init__(self, ctx):
        super(Parameter, self).__init__(ctx)


class Operation(BaseObj):
    """ Operation Object
    """

    __swagger_fields__ = [
        'method',
        'nickname',
        'authorizations',
        'parameters',
        'ResponseMessages',
        'produces',
        'consumes',
        'deprecated'
    ]
    __swagger_data_type_fields__ = True

    def __init__(self, ctx):
        super(Operation, self).__init__(ctx)


class Api(BaseObj):
    """ Api Object
    """

    __swagger_fields__ = ['path', 'operations']

    def __init__(self, ctx):
        super(Api, self).__init__(ctx)


class Property(BaseObj):
    """ Property Object
    """

    __swagger_data_type_fields__ = True

    def __init__(self, ctx):
        super(Property, self).__init__(ctx)


class Model(BaseObj):
    """ Model Object
    """

    __swagger_fields__ = ['id', 'required', 'properties', 'subTypes', 'discriminator']

    def __init__(self, ctx):
        super(Model, self).__init__(ctx)


class Resource(BaseObj):
    """ Resource Object
    """

    __swagger_fields__ = [
        'swaggerVersion',
        'apiVersion',
        'basePath',
        'resourcePath',
        'apis',
        'models',
        'produces',
        'consumes',
        'authorizations']

    def __init__(self, ctx):
        super(Resource, self).__init__(ctx)


class Info(BaseObj):
    """
    """
    def __init__(self, ctx):
        super(Info, self).__init__(ctx)

