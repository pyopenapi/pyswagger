from __future__ import absolute_import
from ..base import BaseObj, FieldMeta
from ...utils import final
from ...io import SwaggerRequest, SwaggerResponse
from ...primitives import Array
import six
import copy


class BaseObj_v2_0(BaseObj):
    __swagger_version__ = '2.0'


class XMLObject(BaseObj_v2_0):
    """ XML Object
    """
    __swagger_fields__ = {
        'name': None,
        'namespace': None,
        'prefix': None,
        'attribute': None,
        'wrapped': None,
    }


class BaseSchema(BaseObj_v2_0):
    """ Base type for Items, Schema, Parameter, Header
    """

    __swagger_fields__ = {
        'type': None,
        'format': None,
        'items': None,
        'default': None,
        'maximum': None,
        'exclusiveMaximum': None,
        'minimum': None,
        'exclusiveMinimum': None,
        'maxLength': None,
        'minLength': None,
        'maxItems': None,
        'minItems': None,
        'multipleOf': None,
        'enum': None,
        'pattern': None,
        'uniqueItems': None,
    }


class Items(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Items Object
    """

    __swagger_fields__ = {
        'collectionFormat': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Schema(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Schema Object
    """

    __swagger_fields__ = {
        '$ref': None,
        'maxProperties': None,
        'minProperties': None,
        'required': [],
        'allOf': [],
        'properties': {},
        'additionalProperties': True,
        'title': None,
        'description': None,
        'discriminator': None,
        'readOnly': None,
        'xml': None,
        'externalDocs': None,
        'example': None,
    }

    __internal_fields__ = {
        # pyswagger only
        'ref_obj': None,
        'final': None,
        'name': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Swagger(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Swagger Object
    """

    __swagger_fields__ = {
        'swagger': None,
        'info': None,
        'host': None,
        'basePath': None,
        'schemes': [],
        'consumes': [],
        'produces': [],
        'paths': None,
        'definitions': None,
        'parameters': None,
        'responses': None,
        'securityDefinitions': None,
        'security': None,
        'tags': None,
        'externalDocs': None,
    }


class Contact(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Contact Object
    """

    __swagger_fields__ = {
        'name': None,
        'url': None,
        'email': None,
    }


class License(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ License Object
    """

    __swagger_fields__ = {
        'name': None,
        'url': None,
    }


class Info(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Info Object
    """

    __swagger_fields__ = {
        'version': None,
        'title': None,
        'description': None,
        'termsOfService': None,
        'contact': None,
        'license': None,
    }


class Parameter(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Parameter Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'name': None,
        'in': None,
        'required': None,

        # body parameter
        'schema': None,

        # other parameter
        'collectionFormat': None,

        # for converter only
        'description': None,

        # TODO: not supported yet
        'allowEmptyValue': False,
    }

    __internal_fields__ = {
        'final': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        i = getattr(self, 'in')
        return prim_factory.produce(self.schema, v, ctx) if i == 'body' else prim_factory.produce(self, v, ctx)


class Header(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Header Object
    """

    __swagger_fields__ = {
        'collectionFormat': None,
        'description': None,
    }

    def _prim_(self, v, prim_factory, ctx=None):
        return prim_factory.produce(self, v, ctx)


class Response(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Response Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'schema': None,
        'headers': {},

        'description': None,
        'examples': None,
    }

    __internal_fields__ = {
        'final': None,
    }


class Operation(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Operation Object
    """

    __swagger_fields__ = {
        'tags': None,
        'operationId': None,
        'consumes': [],
        'produces': [],
        'schemes': [],
        'parameters': None,
        'responses': None,
        'deprecated': False,
        'security': None,
        'description': None,
        'summary': None,
        'externalDocs': None,
    }

    __internal_fields__ = {
        'method': None,
        'url': None,
        'path': None,
        'base_path': None,
        'cached_schemes': [],
    }

    def __call__(self, **k):
        # prepare parameter set
        params = dict(header={}, query=[], path={}, body={}, formData=[], file={})
        names = []
        def _convert_parameter(p):
            if p.name not in k and not p.is_set("default") and p.required:
                raise ValueError('requires parameter: ' + p.name)

            if p.is_set("default"):
                v = k.get(p.name, p.default)
            else:
                if p.name in k:
                    v = k[p.name]
                else:
                    # do not provide value for parameters that use didn't specify.
                    return

            c = p._prim_(v, self._prim_factory, ctx=dict(read=False))
            i = getattr(p, 'in')

            if p.type == 'file':
                params['file'][p.name] = c
            elif i in ('query', 'formData'):
                if isinstance(c, Array):
                    if p.items.type == 'file':
                        params['file'][p.name] = c
                    else:
                        params[i].extend([tuple([p.name, v]) for v in c.to_url()])
                else:
                    params[i].append((p.name, str(c),))
            else:
                params[i][p.name] = str(c) if i != 'body' else c

            names.append(p.name)

        for p in self.parameters:
            _convert_parameter(final(p))

        # check for unknown parameter
        unknown = set(six.iterkeys(k)) - set(names)
        if len(unknown) > 0:
            raise ValueError('Unknown parameters: {0}'.format(unknown))

        return \
        SwaggerRequest(op=self, params=params), SwaggerResponse(self)


class PathItem(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Path Item Object
    """

    __swagger_fields__ = {
        # Reference Object
        '$ref': None,

        'get': None,
        'put': None,
        'post': None,
        'delete': None,
        'options': None,
        'head': None,
        'patch': None,
        'parameters': [],
    }


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Security Scheme Object
    """

    __swagger_fields__ = {
        'type': None,
        'name': None,
        'in': None,
        'flow': None,
        'authorizationUrl': None,
        'tokenUrl': None,
        'scopes': None,
        'description': None,
    }


class Tag(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ Tag Object
    """

    __swagger_fields__ = {
        'name': None,
        'description': None,
        'externalDocs': None,
    }


class ExternalDocumentation(six.with_metaclass(FieldMeta, BaseObj_v2_0)):
    """ External Documentation Object
    """

    __swagger_fields__ = {
        'description': None,
        'url': None,
    }
