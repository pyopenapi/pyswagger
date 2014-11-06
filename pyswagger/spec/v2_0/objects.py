from __future__ import absolute_import
from ...base import BaseObj, FieldMeta
import six


class Items(six.with_metaclass(FieldMeta, BaseObj)):
    """ Items Object
    """

    __swagger_fields__ = [
        ('type', None),
        ('format', None),
        ('items', None),
        ('collectionFormat', None),
        ('default', None),
        ('maximum', None),
        ('exclusiveMaximum', None),
        ('minimum', None),
        ('exclusiveMinimum', None),
        ('maxLength', None),
        ('minLength', None),
        ('pattern', None),
        ('maxItems', None),
        ('minItems', None),
        ('uniqueItems', None),
        ('enum', None),
    ]


class Schema(six.with_metaclass(FieldMeta, BaseObj)):
    """ Schema Object
    """

    __swagger_fields__ = [
        ('$ref', None),
        ('format', None),
        ('default', None),
        ('multipleOf', None),
        ('maximum', None),
        ('exclusiveMaximum', None),
        ('minimum', None),
        ('exclusiveMinimum', None),
        ('maxLength', None),
        ('minLength', None),
        ('pattern', None),
        ('maxItems', None),
        ('minItems', None),
        ('uniqueItems', None),
        ('maxProperties', None),
        ('minProperties', None),
        ('required', None),
        ('enum', None),
        ('type', None),

        ('items', None),
        ('allOf', []),
        ('properties', None),

        ('discriminator', None),
        ('readOnly', None),
    ]


class Swagger(six.with_metaclass(FieldMeta, BaseObj)):
    """ Swagger Object
    """

    __swagger_fields__ = [
        ('swagger', None),
        ('info', None),
        ('host', None),
        ('basePath', None),
        ('schemes', None),
        ('consumes', None),
        ('produces', None),
        ('paths', None),
        ('definitions', None),
        ('parameters', None),
        ('responses', None),
        ('securityDefinitions', None),
        ('security', None),
        ('tags', None),
    ]


class Info(six.with_metaclass(FieldMeta, BaseObj)):
    """ Info Object
    """

    __swagger_fields__ = [
        ('version', None),
    ]


class Parameter(six.with_metaclass(FieldMeta, BaseObj)):
    """ Parameter Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('name', None),
        ('in', None),
        ('required', None),

        # body parameter
        ('schema', None),

        # other parameter
        ('type', None),
        ('format', None),
        ('items', None),
        ('collectionFormat', None),
        ('default', None),
        ('maximum', None),
        ('exclusiveMaximum', None),
        ('minimum', None),
        ('exclusiveMinimum', None),
        ('maxLength', None),
        ('minLength', None),
        ('pattern', None),
        ('maxItems', None),
        ('minItems', None),
        ('uniqueItems', None),
        ('enum', None),
        ('multipleOf', None),
    ]


class Header(six.with_metaclass(FieldMeta, BaseObj)):
    """ Header Object
    """

    __swagger_fields__ = [
        ('type', None),
        ('format', None),
        ('items', None),
        ('collectionFormat', None),
        ('default', None),
        ('maximum', None),
        ('exclusiveMaximum', None),
        ('minimum', None),
        ('exclusiveMinimum', None),
        ('maxLength', None),
        ('minLength', None),
        ('pattern', None),
        ('maxItems', None),
        ('minItems', None),
        ('uniqueItems', None),
        ('enum', None),
        ('multipleOf', None),
    ]


class Response(six.with_metaclass(FieldMeta, BaseObj)):
    """ Response Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('schema', None),
        ('headers', None),
    ]


class Operation(six.with_metaclass(FieldMeta, BaseObj)):
    """ Operation Object
    """

    __swagger_fields__ = [
        ('tags', None),
        ('operationId', None),
        ('consumes', None),
        ('produces', None),
        ('parameters', None),
        ('responses', None),
        ('deprecated', None),
        ('security', None),
    ]


class PathItem(six.with_metaclass(FieldMeta, BaseObj)):
    """ Path Item Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('get', None),
        ('put', None),
        ('post', None),
        ('delete', None),
        ('options', None),
        ('head', None),
        ('patch', None),
        ('parameters', None),
    ]


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj)):
    """ Security Scheme Object
    """

    __swagger_fields__ = [
        ('type', None),
        ('name', None),
        ('in', None),
        ('flow', None),
        ('authorizationUrl', None),
        ('tokenUrl', None),
        ('scopes', None),
    ]


class Tag(six.with_metaclass(FieldMeta, BaseObj)):
    """ Tag Object
    """

    __swagger_fields__ = [
        ('name', None),
    ]

