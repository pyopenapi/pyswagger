from __future__ import absolute_import
from ...base import BaseObj, FieldMeta
from ...utils import deref
from pyswagger import primitives, io
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

    def _prim_(self, v):
        return primitives.prim_factory(self, v)


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

        # pyswagger only
        ('ref_obj', None),
    ]

    def _prim_(self, v):
        return primitives.prim_factory(self, v)


class Swagger(six.with_metaclass(FieldMeta, BaseObj)):
    """ Swagger Object
    """

    __swagger_fields__ = [
        ('swagger', None),
        ('info', None),
        ('host', None),
        ('basePath', None),
        ('schemes', None),
        ('consumes', []),
        ('produces', []),
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

        # pyswagger only
        ('ref_obj', None),
    ]

    def _prim_(self, v):
        return primitives.prim_factory(self, v)


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

        # pyswagger only
        ('ref_obj', None),
    ]


class Operation(six.with_metaclass(FieldMeta, BaseObj)):
    """ Operation Object
    """

    __swagger_fields__ = [
        ('tags', None),
        ('operationId', None),
        ('consumes', []),
        ('produces', []),
        ('parameters', None),
        ('responses', None),
        ('deprecated', None),
        ('security', None),

        # for pyswagger
        ('method', None),
        ('url', None),
    ]

    def __call__(self, **k):
        # prepare parameter set
        params = dict(header={}, query={}, path={}, body={}, formData={}, file={})
        def _convert_parameter(p):
            v = k.get(p.name, p.default)
            if v == None and p.required:
                raise ValueError('requires parameter: ' + p.name)

            c = p._prim_(v)
            i = getattr(p, 'in')
            if i in ('path', 'query'):
                c = six.moves.urllib.parse.quote(str(c))
            elif i == 'header':
                c = str(c)

            params[i if p.type != 'file' else 'file'][p.name] = c

        # TODO: check for unknown parameter
        for p in self.parameters:
            _convert_parameter(deref(p))

        return \
        io.SwaggerRequest(
            params=params,
            produces=self.produces,
            consumes=self.consumes,
            method=self.method,
            url=self.url,
            security=self.security,
            ),
        io.SwaggerResponse(self)


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
        ('parameters', []),

        # pyswagger only
        ('ref_obj', None),
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

