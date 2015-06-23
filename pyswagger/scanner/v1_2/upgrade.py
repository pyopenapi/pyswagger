from __future__ import absolute_import
from ...spec.base import NullContext
from ...scan import Dispatcher
from ...errs import SchemaError
from ...utils import scope_compose, get_or_none
from ...consts import private
from ...spec.v1_2.objects import (
    ResourceList,
    Resource,
    Operation,
    Authorization,
    Parameter,
    Model,
)
from ...spec.v2_0 import objects
import os
import six


def update_type_and_ref(dst, src, scope, sep, app):
    ref = getattr(src, '$ref')
    if ref:
        dst.update_field('$ref', '#/definitions/' + scope_compose(scope, ref, sep=sep))

    if app.prim_factory.is_primitive(getattr(src, 'type', None)):
        dst.update_field('type', src.type.lower())
    elif src.type:
        dst.update_field('$ref', '#/definitions/' + scope_compose(scope, src.type, sep=sep))

def convert_min_max(dst, src):
    def _from_str(name):
        v = getattr(src, name, None)
        if v:
            if src.type == 'integer':
                # we need to handle 1.0 when converting to int
                # that's why we need to convert to float first
                dst.update_field(name, int(float(v)))
            elif src.type == 'number':
                dst.update_field(name, float(v))
            else:
                raise SchemaError('minimum/maximum is only allowed on integer/number, not {0}'.format(src.type))
        else:
            dst.update_field(name, None)

    _from_str('minimum')
    _from_str('maximum')


def convert_schema_from_datatype(obj, scope, sep, app):
    if obj == None:
        return None

    s = objects.Schema(NullContext())
    update_type_and_ref(s, obj, scope, sep, app)
    s.update_field('format', obj.format)
    if obj.is_set('defaultValue'):
        s.update_field('default', obj.defaultValue)
    convert_min_max(s, obj)
    s.update_field('uniqueItems', obj.uniqueItems)
    s.update_field('enum', obj.enum)
    if obj.items:
        i = objects.Schema(NullContext())
        update_type_and_ref(i, obj.items, scope, sep, app)
        i.update_field('format', obj.items.format)
        s.update_field('items', i)

    return s

def convert_items(o, app):
    item = objects.Items(NullContext())
    if getattr(o, '$ref'):
        raise SchemaError('Can\'t have $ref for Items')
    if not app.prim_factory.is_primitive(getattr(o, 'type', None)):
        raise SchemaError('Non primitive type is not allowed for Items')
    item.update_field('type', o.type.lower())
    item.update_field('format', o.format)

    return item


class Upgrade(object):
    """ convert 1.2 object to 2.0 object
    """
    class Disp(Dispatcher): pass

    def __init__(self, sep=private.SCOPE_SEPARATOR):
        self.__swagger = None
        self.__sep = sep

    @Disp.register([ResourceList])
    def _resource_list(self, path, obj, app):
        o = objects.Swagger(NullContext())

        #   Info Object
        info = objects.Info(NullContext())
        info.update_field('version', obj.apiVersion)
        info.update_field('title', get_or_none(obj, 'info','title'))
        info.update_field('description', get_or_none(obj, 'info', 'description'))
        info.update_field('termsOfService', get_or_none(obj, 'info', 'termsOfServiceUrl'))
        #       Contact Object
        if obj.info.contact:
            contact = objects.Contact(NullContext())
            contact.update_field('email', get_or_none(obj, 'info', 'contact'))
            info.update_field('contact', contact)
        #       License Object
        if obj.info.license or obj.info.licenseUrl:
            license = objects.License(NullContext())
            license.update_field('name', get_or_none(obj, 'info', 'license'))
            license.update_field('url', get_or_none(obj, 'info', 'licenseUrl'))
            info.update_field('license', license)

        o.update_field('info', info)

        o.update_field('swagger', '2.0')
        o.update_field('schemes', ['http', 'https'])

        o.update_field('host', '')

        o.update_field('basePath', '')
        o.update_field('tags', [])
        o.update_field('definitions', {})
        o.update_field('parameters', {})
        o.update_field('responses', {})
        o.update_field('paths', {})
        o.update_field('security', [])
        o.update_field('securityDefinitions', {})

        o.update_field('consumes', [])
        o.update_field('produces', [])

        self.__swagger = o

    @Disp.register([Resource])
    def _resource(self, path, obj, app):
        name = obj.get_name(path)
        for t in self.__swagger.tags:
            if t.name == name:
                break
        else:
            tt = objects.Tag(NullContext())
            tt.update_field('name', name)
            self.__swagger.tags.append(tt)

    @Disp.register([Operation])
    def _operation(self, path, obj, app):
        o = objects.Operation(NullContext())
        scope = obj._parent_.get_name(path)

        o.update_field('tags', [scope])
        o.update_field('operationId', obj.nickname)
        o.update_field('summary', obj.summary)
        o.update_field('description', obj.notes)
        o.update_field('deprecated', obj.deprecated == 'true')

        c = obj.consumes if obj.consumes and len(obj.consumes) > 0 else obj._parent_.consumes
        o.update_field('consumes', c if c else [])

        p = obj.produces if obj.produces and len(obj.produces) > 0 else obj._parent_.produces
        o.update_field('produces', p if p else [])

        o.update_field('parameters', [])
        o.update_field('security', [])
        # if there is not authorizations in this operation,
        # looking for it in resource object.
        _auth = obj.authorizations if obj.authorizations and len(obj.authorizations) > 0 else obj._parent_.authorizations
        if _auth:
            for name, scopes in six.iteritems(_auth):
                o.security.append({name: [v.scope for v in scopes]})

        # Operation return value
        o.update_field('responses', {})
        resp = objects.Response(NullContext())
        if obj.type != 'void':
            resp.update_field('schema', convert_schema_from_datatype(obj, scope, self.__sep, app))
        o.responses['default'] = resp

        path = obj._parent_.basePath + obj.path
        if path not in self.__swagger.paths:
            self.__swagger.paths[path] = objects.PathItem(NullContext())
 
        method = obj.method.lower()
        self.__swagger.paths[path].update_field(method, o)

    @Disp.register([Authorization])
    def _authorization(self, path, obj, app):
        o = objects.SecurityScheme(NullContext())

        if obj.type == 'basicAuth':
            o.update_field('type', 'basic')
        else:
            o.update_field('type', obj.type)
        o.update_field('scopes', {})
        for s in obj.scopes or []:
            o.scopes[s.scope] = s.description

        if o.type == 'oauth2':
            o.update_field('authorizationUrl', get_or_none(obj, 'grantTypes', 'implicit', 'loginEndpoint', 'url'))
            o.update_field('tokenUrl', get_or_none(obj, 'grantTypes', 'authorization_code', 'tokenEndpoint', 'url'))
            if o.authorizationUrl:
                o.update_field('flow', 'implicit')
            elif o.tokenUrl:
                o.update_field('flow', 'access_code')
        elif o.type == 'apiKey':
            o.update_field('name', obj.keyname)
            o.update_field('in', obj.passAs)

        self.__swagger.securityDefinitions[obj.get_name(path)] = o

    @Disp.register([Parameter])
    def _parameter(self, path, obj, app):
        o = objects.Parameter(NullContext())
        scope = obj._parent_._parent_.get_name(path)

        o.update_field('name', obj.name)
        o.update_field('required', obj.required)
        o.update_field('description', obj.description)

        if obj.paramType == 'form':
            o.update_field('in', 'formData')
        else:
            o.update_field('in', obj.paramType)

        if 'body' == getattr(o, 'in'):
            o.update_field('schema', convert_schema_from_datatype(obj, scope, self.__sep, app))
        else:
            if getattr(obj, '$ref'):
                raise SchemaError('Can\'t have $ref in non-body Parameters')

            if obj.allowMultiple == True and obj.items == None:
                o.update_field('type', 'array')
                o.update_field('collectionFormat', 'csv')
                o.update_field('uniqueItems', obj.uniqueItems)
                o.update_field('items', convert_items(obj, app))
                if obj.is_set("defaultValue"):
                    o.update_field('default', [obj.defaultValue])
                o.items.update_field('enum', obj.enum)
            else:
                o.update_field('type', obj.type.lower())
                o.update_field('format', obj.format)
                if obj.is_set("defaultValue"):
                    o.update_field('default', obj.defaultValue)
                convert_min_max(o, obj)
                o.update_field('enum', obj.enum)

            if obj.items:
                o.update_field('collectionFormat', 'csv')
                o.update_field('uniqueItems', obj.uniqueItems)
                o.update_field('items', convert_items(obj.items, app))

        path = obj._parent_._parent_.basePath + obj._parent_.path 
        method = obj._parent_.method.lower()
        op = getattr(self.__swagger.paths[path], method)
        op.parameters.append(o)

    @Disp.register([Model])
    def _model(self, path, obj, app):
        scope = obj._parent_.get_name(path)

        s = scope_compose(scope, obj.get_name(path), sep=self.__sep)
        o = self.__swagger.definitions.get(s, None)
        if not o:
            o = objects.Schema(NullContext())
            self.__swagger.definitions[s] = o

        props = {}
        for name, prop in six.iteritems(obj.properties):
            props[name] = convert_schema_from_datatype(prop, scope, self.__sep, app)
            props[name].update_field('description', prop.description)
        o.update_field('properties', props)
        o.update_field('required', obj.required)
        o.update_field('discriminator', obj.discriminator)
        o.update_field('description', obj.description)

        for t in obj.subTypes or []:
            # here we assume those child models belongs to
            # the same resource.
            sub_s = scope_compose(scope, t, sep=self.__sep)
            sub_o = self.__swagger.definitions.get(sub_s, None)
            if not sub_o:
                sub_o = objects.Schema(NullContext())
                self.__swagger.definitions[sub_s] = sub_o

            new_ref = objects.Schema(NullContext())
            new_ref.update_field('$ref', '#/definitions/' + s)
            sub_o.allOf.append(new_ref)

    @property
    def swagger(self):
        """ some preparation before returning Swagger object
        """
        # prepare Swagger.host & Swagger.basePath
        if not self.__swagger:
            return None

        common_path = os.path.commonprefix(self.__swagger.paths.keys())
        # remove tailing slash,
        # because all paths in Paths Object would prefixed with slah.
        common_path = common_path[:-1] if common_path[-1] == '/' else common_path

        if len(common_path) > 0:
            p = six.moves.urllib.parse.urlparse(common_path)
            self.__swagger.update_field('host', p.netloc)

            new_common_path = six.moves.urllib.parse.urlunparse((
                p.scheme, p.netloc, '', '', '', ''))
            new_path = {}
            for k in self.__swagger.paths.keys():
                new_path[k[len(new_common_path):]] = self.__swagger.paths[k]
            self.__swagger.update_field('paths', new_path)

        return self.__swagger
