from __future__ import absolute_import
from .base import BaseObj


class Scope(BaseObj):
    """ Scope Object
    """

    __swagger_fields__ = ['scope']


class LoginEndpoint(BaseObj):
    """ LoginEndpoint Object
    """

    __swagger_fields__ = ['url']


class Implicit(BaseObj):
    """ Implicit Object
    """

    __swagger_fields__ = ['loginEndpoint', 'tokenName']


class TokenRequestEndpoint(BaseObj):
    """ TokenRequestEndpoint Object
    """

    __swagger_fields__ = ['url', 'clientIdName', 'clientSecretName']


class TokenEndpoint(BaseObj):
    """ TokenEndpoint Object
    """

    __swagger_fields__ = ['url', 'tokenName']


class AuthorizationCode(BaseObj):
    """ AuthorizationCode Object
    """

    __swagger_fields__ = ['tokenRequestEndpoint', 'tokenEndpoint']


class GrantType(BaseObj):
    """ GrantType Object
    """

    __swagger_fields__ = ['implicit', 'authorization_code']


class Authorizations(BaseObj):
    """ Authorizations Object
    """

    __swagger_fields__ = ['scope']


class Authorization(BaseObj):
    """ Authorization Object
    """

    __swagger_fields__ = ['type', 'passAs', 'keyname', 'scopes', 'grantTypes']


class ResponseMessage(BaseObj):
    """ ResponseMessage Object
    """

    __swagger_fields__ = ['code', 'message', 'responseModel']


class Parameter(BaseObj):
    """ Parameter Object
    """

    __swagger_fields__ = ['paramType', 'name', 'required', 'allowMultiple']
    __swagger_data_type_fields__ = True


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


class Api(BaseObj):
    """ Api Object
    """

    __swagger_fields__ = ['path', 'operations']


class Property(BaseObj):
    """ Property Object
    """

    __swagger_data_type_fields__ = True


class Model(BaseObj):
    """ Model Object
    """

    __swagger_fields__ = ['id', 'required', 'properties', 'subTypes', 'discriminator']


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


class Info(BaseObj):
    """
    """

    __swagger_fields__ = ['title', 'termsOfServiceUrl', 'contact', 'license', 'licenseUrl']
