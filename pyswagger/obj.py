from __future__ import absolute_import
from .base import BaseObj, DataTypeObj, FieldMeta
from .base import Items # make caller import from here
import six


class Scope(six.with_metaclass(FieldMeta, BaseObj)):
    """ Scope Object
    """

    __swagger_fields__ = ['scope']


class LoginEndpoint(six.with_metaclass(FieldMeta, BaseObj)):

    """ LoginEndpoint Object
    """

    __swagger_fields__ = ['url']


class Implicit(six.with_metaclass(FieldMeta, BaseObj)):

    """ Implicit Object
    """

    __swagger_fields__ = ['loginEndpoint', 'tokenName']


class TokenRequestEndpoint(six.with_metaclass(FieldMeta, BaseObj)):

    """ TokenRequestEndpoint Object
    """

    __swagger_fields__ = ['url', 'clientIdName', 'clientSecretName']


class TokenEndpoint(six.with_metaclass(FieldMeta, BaseObj)):

    """ TokenEndpoint Object
    """

    __swagger_fields__ = ['url', 'tokenName']


class AuthorizationCode(six.with_metaclass(FieldMeta, BaseObj)):

    """ AuthorizationCode Object
    """

    __swagger_fields__ = ['tokenRequestEndpoint', 'tokenEndpoint']


class GrantType(six.with_metaclass(FieldMeta, BaseObj)):

    """ GrantType Object
    """

    __swagger_fields__ = ['implicit', 'authorization_code']


class Authorizations(six.with_metaclass(FieldMeta, BaseObj)):

    """ Authorizations Object
    """

    __swagger_fields__ = ['scope']


class Authorization(six.with_metaclass(FieldMeta, BaseObj)):

    """ Authorization Object
    """

    __swagger_fields__ = ['type', 'passAs', 'keyname', 'scopes', 'grantTypes']


class ResponseMessage(six.with_metaclass(FieldMeta, BaseObj)):

    """ ResponseMessage Object
    """

    __swagger_fields__ = ['code', 'message', 'responseModel']


class Parameter(six.with_metaclass(FieldMeta, DataTypeObj)):
    """ Parameter Object
    """

    __swagger_fields__ = ['paramType', 'name', 'required', 'allowMultiple']


class Operation(six.with_metaclass(FieldMeta, DataTypeObj)):
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
        'deprecated',

        # path from Api object
        'path'
    ]


class Api(six.with_metaclass(FieldMeta, BaseObj)):

    """ Api Object
    """

    __swagger_fields__ = ['path', 'operations']


class Property(six.with_metaclass(FieldMeta, DataTypeObj)):
    """ Property Object
    """

    __swagger_fields__ = []


class Model(six.with_metaclass(FieldMeta, BaseObj)):

    """ Model Object
    """

    __swagger_fields__ = ['id', 'required', 'properties', 'subTypes', 'discriminator']


class Resource(six.with_metaclass(FieldMeta, BaseObj)):

    """ Resource Object
    """

    __swagger_fields__ = [
        'swaggerVersion',
        'apiVersion',
        'apis',
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

                op.update_field('path', api.path)
                new_api[name] = op

        self.update_field('apis', new_api)


class Info(six.with_metaclass(FieldMeta, BaseObj)):

    """ Info Object
    """

    __swagger_fields__ = ['title', 'termsOfServiceUrl', 'contact', 'license', 'licenseUrl']


class ResourceList(six.with_metaclass(FieldMeta, BaseObj)):
    """ Resource List Object
    """
    __swagger_fields__ = ['swaggerVersion', 'apis', 'apiVersion', 'info', 'authorizations']

