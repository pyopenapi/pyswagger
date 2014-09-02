from __future__ import absolute_import
from ..scan import Dispatcher
from ..utils import scope_compose
from ..obj import (
    DataTypeObj,
    Parameter,
    Property,
    Items,
    Authorization,
    Operation,
    GrantType,
    Scope,
    Authorizations,
    LoginEndpoint,
    Implicit,
    TokenRequestEndpoint,
    TokenEndpoint,
    AuthorizationCode,
    ResponseMessage,
    Api,
    Model,
    Resource,
    Info,
    ResourceList
    )
import six


class Validate(object):
    """
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.errs = []

    @Disp.register([DataTypeObj])
    def _validate_data(self, scope, name, obj, _):
        """ convert string value to integer/float value """
        errs = []

        if obj.type == None and obj.ref == None:
            errs.append('type or $ref should be existed.')

        # make sure there is 'item' along with 'array'
        if not (obj.type == 'array') == (obj.items != None):
            errs.append('array should be existed along with items')
        if obj.uniqueItems != None and obj.type != 'array':
            errs.append('uniqueItems is only used for array type.')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([Parameter])
    def _validate_param(self, scope, name, obj, _):
        """ validate option combination of Parameter object """
        errs = []

        if obj.allowMultiple:
            if not obj.paramType in ('path', 'query', 'header'):
                errs.append('allowMultiple should be applied on path, header, or query parameters')
            if obj.type == 'array':
                errs.append('array Type with allowMultiple is not supported.')

        if obj.paramType == 'body' and obj.name not in ('', 'body'):
            errs.append('body parameter with invalid name: {0}'.format(obj.name))

        if obj.type == 'File':
            if obj.paramType != 'form':
                errs.append('File parameter should be form type: {0}'.format(obj.name))
            if 'multipart/form-data' not in obj._parent_.consumes:
                errs.append('File parameter should consume multipart/form-data: {0}'.format(obj.name))

        if obj.type == 'void':
            errs.append('void is only allowed in Operation object.')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([Property])
    def _validate_prop(self, scope, name, obj, _):
        """ validate option combination of Property object """
        errs = []

        if obj.type == 'void':
            errs.append('void is only allowed in Operation object.')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([Items])
    def _validate_items(self, scope, name, obj, _):
        """ validate option combination of Property object """
        errs = []

        if obj.type == 'void':
            errs.append('void is only allowed in Operation object.')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([Authorization])
    def _validate_auth(self, scope, name, obj, _):
        """ validate that apiKey and oauth2 requirements """
        errs = []

        if obj.type == 'apiKey':
            if not obj.passAs:
                errs.append('need "passAs" for apiKey')
            if not obj.keyname:
                errs.append('need "keyname" for apiKey')

        elif obj.type == 'oauth2':
            if not obj.grantTypes:
                errs.append('need "grantTypes" for oauth2')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([GrantType])
    def _validate_granttype(self, scope, name, obj, _):
        """ make sure either implicit or authorization_code is defined """
        errs = []

        if not obj.implicit and not obj.authorization_code:
            errs.append('Either implicit or authorization_code should be defined.')

        return '' if scope == None else scope, name, obj.__class__.__name__, errs


    @Disp.register([Operation])
    def _validate_auths(self, scope, name, obj, app):
        """ make sure that apiKey and basicAuth are empty list
        in Operation object.
        """
        errs = []

        for k, v in six.iteritems(obj.authorizations):
            if k not in app.schema.authorizations:
                errs.append('auth {0} not found in resource list'.format(k))

            if app.schema.authorizations[k].type in ('basicAuth', 'apiKey') and v != []:
                errs.append('auth {0} should be an empty list'.format(k))

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    """ requirement """

    @staticmethod
    def _check_reqs(scope, name, obj, reqs):
        errs = []
        for r in reqs:
           if not hasattr(obj, r) or None == getattr(obj, r):
                errs.append('requirement {0} not meet.'.format(r))

        return '' if scope == None else scope, name, obj.__class__.__name__, errs

    @Disp.register([Scope])
    def scope_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['scope'])

    @Disp.register([Authorizations])
    def authorizations_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['scope'])

    @Disp.register([LoginEndpoint])
    def login_endpoint_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['url'])

    @Disp.register([Implicit])
    def implicit_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['loginEndpoint'])

    @Disp.register([TokenRequestEndpoint])
    def token_request_endpoint_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['url'])

    @Disp.register([TokenEndpoint])
    def token_endpoint_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['url'])

    @Disp.register([AuthorizationCode])
    def authorization_code_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['tokenRequestEndpoint', 'tokenEndpoint'])


    @Disp.register([Authorization])
    def authorization_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['type'])

    @Disp.register([ResponseMessage])
    def response_message_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['code', 'message'])

    @Disp.register([Parameter])
    def parameter_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['paramType', 'name'])

    @Disp.register([Operation])
    def operation_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['method', 'nickname', 'parameters'])

    @Disp.register([Api])
    def api_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['path', 'operations'])

    @Disp.register([Model])
    def model_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['id', 'properties'])

    @Disp.register([Resource])
    def resource_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['swaggerVersion', 'basePath', 'apis'])

    @Disp.register([ResourceList])
    def resource_list_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['swaggerVersion', 'apis'])

    @Disp.register([Info])
    def info_require(self, scope, name, obj, _):
        return self._check_reqs(scope, name, obj, ['title', 'description'])

    @Disp.result
    def result(self, result):
        """ aggregate result """
        if result:
            if len(result[3]) == 0:
                return
        else:
            return

        key = (scope_compose(result[0], result[1]), result[2])
        self.errs.extend([(key, err) for err in result[3]])

