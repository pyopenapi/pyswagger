from __future__ import absolute_import
from .base import BaseObj, DataTypeObj
from .base import Items # make caller import from here


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


class Parameter(DataTypeObj):
    """ Parameter Object
    """

    __swagger_fields__ = ['paramType', 'name', 'required', 'allowMultiple']


class Operation(DataTypeObj):
    """ Operation Object
    """

    __swagger_fields__ = [
        'method',
        'nickname',
        'authorizations',
        'parameters',
        'responseMessages',
        'produces',
        'consumes',
        'deprecated'
    ]


class Api(BaseObj):
    """ Api Object
    """

    __swagger_fields__ = ['path', 'operations']


class Property(DataTypeObj):
    """ Property Object
    """

    __swagger_fields__ = []


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
        'models',
        'produces',
        'consumes',
        'authorizations']

    def __init__(self, ctx):
        """ The original structure of API object is very bad
        for seeking nickname for operations. Since nickname is unique
        in one Resource, we can just make it flat.
        """
        super(Resource, self).__init__(ctx)

        new_api = {}
        for api in ctx._obj['apis']:
            for op in api.operations:
                name = op.nickname
                if name in new_api.keys():
                    raise ValueError('duplication operation found: ' + name)

                op.add_field('path', api.path)
                new_api[name] = op

        self.add_field('apis', new_api)


class Info(BaseObj):
    """
    """

    __swagger_fields__ = ['title', 'termsOfServiceUrl', 'contact', 'license', 'licenseUrl']
