from __future__ import absolute_import
from ...base import NullContext
from ...scan import Dispatcher
from ...utils import scope_compose
from ...spec.v1_2.objects import (
    ResourceList,
    Resource,
    Operation,
    Authorization,
    Parameter,
    Model
)
from pyswagger import objects
import os
import six

def convert_schema_from_datatype(obj):
    s = objects.Schema(NullContext())

    s.update_field('$ref', getattr(obj, '$ref'))
    s.update_field('type', obj.type)
    s.update_field('format', obj.format)
    s.update_field('default', obj.defaultValue)
    s.update_field('maximum', obj.maximum)
    s.update_field('minimum', obj.minimum)
    s.update_field('uniqueItems', obj.uniqueItems)
    s.update_field('enum', obj.enum)

    if obj.items:
        i = objects.Item(NullContext())
        i.update_field('type', obj.items.type)
        i.update_field('format', obj.items.format)
        s.update_field('items', i)

    return s


def update_ref(dst, src):
    ref = getattr(src, '$ref')
    if ref:
        src.update_field('$ref', '#/definitions/' + ref)


class Upgrade(object):
    """ convert 1.2 object to 2.0 object
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.__swagger = None

    @Disp.register([ResourceList])
    def _resource_list(self, scope, name, obj, app):
        o = objects.Swagger(NullContext())

        info = objects.Info(NullContext())
        info.update_field('version', obj.apiVersion)
        o.update_field('info', info)

        o.update_field('swagger', obj.swaggerVersion)
        o.update_field('schemes', ['http', 'https'])

        o.update_field('host', '')

        o.update_field('basePath', '')
        o.update_field('tags', [])
        o.update_field('definitions', {})
        o.update_field('parameters', {})
        o.update_field('responses', {})
        o.update_field('paths', {})
        o.update_field('security', {})

        o.update_field('consumes', [])
        o.update_field('produces', [])

        self.__swagger = o

    @Disp.register([Resource])
    def _resource(self, scope, name, obj, app):
        o = objects.PathItem(NullContext())

        if obj.consumes:
            self.__swagger.update_field('consumes', list(set(self.__swagger.consumes + obj.consumes)))
        if obj.produces:
            self.__swagger.update_field('produces', list(set(self.__swagger.produces + obj.produces)))

        self.__swagger.paths[obj.basePath + obj.resourcePath] = o
        self.__swagger.tags.append(name)

    @Disp.register([Operation])
    def _operation(self, scope, name, obj, app):
        o = objects.Operation(NullContext())

        o.update_field('tags', [scope])
        o.update_field('operationId', obj.nickname)
        o.update_field('consumes', obj.consumes)
        o.update_field('produces', obj.produces)

        o.update_field('parameters', [])
        o.update_field('responses', {})
        o.update_field('security', obj.authorizations)

        # Operation return value
        resp = objects.Response(NullContext())
        resp.update_field('schema', convert_schema_from_datatype(obj))
        o.responses['default'] = resp

        path = obj._parent_.basePath + obj._parent_.resourcePath 
        method = obj.method.lower()
        self.__swagger.paths[path].update_field(method, o)

    @Disp.register([Authorization])
    def _authorization(self, scope, name, obj, app):
        o = objects.SecurityScheme(NullContext())

        if obj.type == 'basicAuth':
            o.update_field('type', 'basic')
        else:
            o.update_field('type', obj.type)
        o.update_field('name', obj.keyname)
        o.update_field('in', obj.passAs)
        o.update_field('authorizationUrl', obj.grantTypes.implicit.loginEndpoint.url)
        o.update_field('tokenUrl', obj.grantTypes.authorization_code.tokenEndpoint.url)

        o.update_field('scopes', {})
        for s in obj.scopes:
            o.scopes[s.scope] = ''

        o.update_field('flow', '')
        if o.type == 'oauth2':
            if o.authorizationUrl:
                o.update_field('flow', 'implicit')
            elif o.tokenUrl:
                o.update_field('flow', 'accessCode')

        self.__swagger.security[name] = o

    @Disp.register([Parameter])
    def _parameter(self, scope, name, obj, app):
        o = objects.Parameter(NullContext())

        update_ref(o, obj)
        o.update_field('name', obj.name)
        if obj.paramType == 'form':
            o.update_field('in', 'formData')
        else:
            o.update_field('in', obj.paramType)

        o.update_field('in', obj.paramType)
        o.update_field('required', obj.required)

        if 'body' == getattr(o, 'in'):
            o.update_field('schema', convert_schema_from_datatype(obj))
        else:
            o.update_field('type', obj.type)
            o.update_field('format', obj.format)
            o.update_field('collectionFormat', 'csv')
            o.update_field('default', obj.defaultValue)
            o.update_field('maximum', obj.maximum)
            o.update_field('minimum', obj.minimum)
            o.update_field('uniqueItems', obj.uniqueItems)
            o.update_field('enum', obj.enum)

            if obj.items:
                item = objects.Items(NullContext())
                update_ref(item, obj.items)
                item.update_field('$ref', '#/definitions/' + getattr(obj.items, '$ref'))
                item.update_field('type', obj.items.type)
                item.update_field('format', obj.items.format)

                o.update_field('items', item)

        path = obj._parent_._parent_.basePath + obj._parent_._parent_.resourcePath 
        method = obj._parent_.method.lower()
        op = getattr(self.__swagger.paths[path], method)
        op.parameters.append(o)

    @Disp.register([Model])
    def _model(self, scope, name, obj, app):
        s = scope_compose(scope, name)
        o = self.__swagger.definitions.get(s, None)
        if not o:
            o = objects.Schema(NullContext())

        props = {}
        for name, prop in obj.properties.iteritems():
            props[name] = convert_schema_from_datatype(prop)
        o.update_field('properties', props)
        o.update_field('required', obj.required)
        o.update_field('discriminator', obj.discriminator)
        o.update_field('allOf', [])

        for t in obj.subTypes or []:
            # here we assume those child models belongs to
            # the same resource.
            sub_s = scope_compose(scope, t)

            sub_o = self.__swagger.definitions.get(sub_s, None)
            if not sub_o:
                sub_o = objects.Schema(NullContext())

            new_ref = objects.Schema(NullContext())
            new_ref.update_field('$ref', '#/definitions/' + s)
            sub_o.allOf.append(new_ref)

        self.__swagger.definitions[s] = o

    @property
    def swagger(self):
        """ some preparation before returning Swagger object
        """
        # prepare Swagger.host & Swagger.basePath
        if not self.__swagger:
            return None

        common_path = os.path.commonprefix(self.__swagger.paths.keys())
        if len(common_path) > 0:
            p = six.moves.urllib.parse.urlparse(common_path)
            self.__swagger.update_field('host', p.netloc)
            self.__swagger.update_field('basePath', p.path)

        return self.__swagger
