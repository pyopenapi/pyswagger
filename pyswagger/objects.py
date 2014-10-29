from __future__ import absolute_import
from .base import BaseObj, FieldMeta
import six


class Items(six.with_metaclass(FieldMeta, BaseObj)):
    """ Items Object
    """

    __swagger_fields__ = [
        'type',
        'format',
        'items',
        'collectionFormat',
        'default',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'enum'
    ]


class Schema(six.with_metaclass(FieldMeta, BaseObj)):
    """ Schema Object
    """

    __swagger_fields__ = [
        '$ref',
        'format',
        'default',
        'multipleOf',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'maxProperties',
        'minProperties',
        'required',
        'enum',
        'type',

        'items',
        'allOf',
        'properties',

        'discriminator',
        'readOnly',
    ]


class Swagger(six.with_metaclass(FieldMeta, BaseObj)):
    """ Swagger Object
    """

    __swagger_fields__ = [
        'swagger',
        'info',
        'host',
        'basePath',
        'schemes',
        'consumes',
        'produces',
        'paths',
        'definitions',
        'parameters',
        'responses',
        'securityDefinitions',
        'security',
        'tags',
    ]


class Info(six.with_metaclass(FieldMeta, BaseObj)):
    """ Info Object
    """

    __swagger_fields__ = ['version']


class Parameter(six.with_metaclass(FieldMeta, BaseObj)):
    """ Parameter Object
    """

    __swagger_fields__ = [
        # Reference Object
        '$ref',

        'name',
        'in',
        'required',

        # body parameter
        'schema',

        # other parameter
        'type',
        'format',
        'items',
        'collectionFormat',
        'default',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'enum',
        'multipleOf',
    ]


class Header(six.with_metaclass(FieldMeta, BaseObj)):
    """ Header Object
    """

    __swagger_fields__ = [
        'type',
        'format',
        'items',
        'collectionFormat',
        'default',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'enum',
        'multipleOf',
    ]


class Response(six.with_metaclass(FieldMeta, BaseObj)):
    """ Response Object
    """

    __swagger_fields__ = [
        # Reference Object
        '$ref',

        'schema',
        'headers',
    ]


class Operation(six.with_metaclass(FieldMeta, BaseObj)):
    """ Operation Object
    """

    __swagger_fields__ = [
        'tags',
        'operationId',
        'consumes',
        'produces',
        'parameters',
        'responses',
        'deprecated',
        'security'
    ]


class PathItem(six.with_metaclass(FieldMeta, BaseObj)):
    """ Path Item Object
    """

    __swagger_fields__ = [
        # Reference Object
        '$ref',

        'get',
        'put',
        'post',
        'delete',
        'options',
        'head',
        'patch',
        'parameters',
    ]


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj)):
    """ Security Scheme Object
    """

    __swagger_fields__ = [
        'type',
        'name',
        'in',
        'flow',
        'authorizationUrl',
        'tokenUrl',
        'scopes',
    ]


class Tag(six.with_metaclass(FieldMeta, BaseObj)):
    """ Tag Object
    """

    __swagger_fields__ = ['name']

