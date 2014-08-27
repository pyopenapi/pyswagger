from __future__ import absolute_import
from .base import BaseObj, FieldMeta, Context
from .io import SwaggerRequest, SwaggerResponse
from pyswagger import prim
import six


class Items(six.with_metaclass(FieldMeta, BaseObj)):
    """ Items Object
    """
    __swagger_fields__ = ['type', '$ref']
    __swagger_rename__ = {'$ref': 'ref'}

    def _prim_(self, v):
        return prim.prim_factory(self, v)


class ItemsContext(Context):
    """ Context of Items Object
    """
    __swagger_ref_object__ = Items
    __swagger_required__ = []


class DataTypeObj(BaseObj):
    """ Data Type Fields
    """
    __swagger_fields__ = [
        'type',
        '$ref',
        'format',
        'defaultValue',
        'enum',
        'items',
        'minimum',
        'maximum',
        'uniqueItems'
    ]
    __swagger_rename__ = {'$ref': 'ref'}

    def __init__(self, ctx):
        super(DataTypeObj, self).__init__(ctx)

        # Items Object, too lazy to create a Context for DataTypeObj
        # to wrap this child.
        with ItemsContext(ctx._obj, 'items') as items_ctx:
            items_ctx.parse(ctx._obj.get('items', None))

        type_fields = set(DataTypeObj.__swagger_fields__) - set(ctx.__swagger_required__)
        for field in type_fields:
            # almost every data field is not required.
            self.update_field(field, ctx._obj.get(field, None))

    def _prim_(self, v):
        return prim.prim_factory(self, v)


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

    def _prim_(self, v):
        return prim.prim_factory(self, v, self.allowMultiple)


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

        # path from Api object, concated with Resource object
        'path'
    ]

    def __call__(self, **kwargs):
        req = SwaggerRequest(self, params=kwargs,
            produces=self._parent_.produces,
            consumes=self._parent_.consumes,
            authorizations=self._parent_.authorizations)
        return req, SwaggerResponse(self)


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

    __swagger_fields__ = [
        'id',
        'required',
        'properties',
        'subTypes',
        'discriminator',

        # for model inheritance
        '_extends_'
        ]

    def _prim_(self, v):
        return prim.Model(self, v)


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
            new_path = self.basePath + api.path
            for op in api.operations:
                name = op.nickname
                if name in new_api.keys():
                    raise ValueError('duplication operation found: ' + name)

                # Operation objects now have 'path' attribute.
                op.update_field('path', new_path)
                # Operation objects' parent is now Resource object(API Declaration).
                op._parent__ = self
                new_api[name] = op

        # replace Api with Operations
        self.update_field('apis', new_api)


class Info(six.with_metaclass(FieldMeta, BaseObj)):
    """ Info Object
    """

    __swagger_fields__ = ['title', 'termsOfServiceUrl', 'contact', 'license', 'licenseUrl']


class ResourceList(six.with_metaclass(FieldMeta, BaseObj)):
    """ Resource List Object
    """
    __swagger_fields__ = ['swaggerVersion', 'apis', 'apiVersion', 'info', 'authorizations']

