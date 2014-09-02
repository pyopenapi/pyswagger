from __future__ import absolute_import
from .getter import HttpGetter, FileGetter
from .parser import ResourceListContext
from .scan import Scanner
from .scanner import Validate, TypeReduce, Resolve, FixMinMax
from .utils import ScopeDict
import inspect
import base64
import six


class SwaggerApp(object):
    """ Resource Listing
    """
    @property
    def schema(self):
        return self.__schema

    @property
    def rs(self):
        return self.__resrc

    @property
    def op(self):
        return self.__op

    @property
    def m(self):
        return self.__m

    def validate(self, strict=True):
        """
        """
        s = Scanner(self)
        v = Validate()

        s.scan(route=[v])

        if strict and len(v.errs) > 0:
            raise ValueError('this Swagger App contains error: {0}.'.format(len(v.errs)))

        return v.errs

    @classmethod
    def _create_(kls, url, getter=None):
        """
        """

        local_getter = getter or HttpGetter
        p = six.moves.urllib.parse.urlparse(url)
        if p.scheme == "":
            if p.netloc == "" and p.path != "":
                # it should be a file path
                local_getter = FileGetter(p.path)
            else:
                raise ValueError('url should be a http-url or file path -- ' + url)

        if inspect.isclass(local_getter):
            # default initialization is passing the url
            # you can override this behavior by passing an
            # initialized getter object.
            local_getter = local_getter(url)

        tmp = {'_tmp_': {}}
        with ResourceListContext(tmp, '_tmp_', local_getter) as ctx:
            ctx.parse()

        app = kls()
        # __schema
        setattr(app, '_' + kls.__name__ + '__schema', tmp['_tmp_'])
        # __resrc
        setattr(app, '_' + kls.__name__ + '__resrc', app.schema.apis)

        # reducer for Operation & Model
        tr = TypeReduce()

        # convert types
        s = Scanner(app)
        s.scan(route=[FixMinMax(), tr])

        # 'm' for model
        setattr(app, '_' + kls.__name__ + '__m', ScopeDict(tr.model))
        # 'op' for operation
        setattr(app, '_' + kls.__name__ + '__op', ScopeDict(tr.op))

        # resolve reference
        s.scan(route=[Resolve()])

        return app


class SwaggerAuth(object):
    """ authorization handler """

    def __init__(self, app):
        self.__app = app
        self.__auths = {}

    def update_with(self, name, auth_info):
        """
        """
        auth = self.__app.schema.authorizations.get(name, None)
        if auth == None:
            raise ValueError('Unknown authorization name: [{0}]'.format(name))

        cred = auth_info
        header = True
        if auth.type == 'basicAuth':
            cred = 'Basic ' + base64.standard_b64encode(six.b('{0}:{1}'.format(*auth_info))).decode('utf-8')
            key = 'Authorization'
        elif auth.type == 'apiKey':
            key = auth.keyname
            header = auth.passAs == 'header'
        elif auth.type == 'oauth2':
            if auth.grantTypes.implicit:
                key = auth.grantTypes.implicit.tokenName
            else:
                key = auth.grantTypes.authorization_code.tokenEndpoint.tokenName
            key = key if key else 'access_token'
        else:
            raise ValueError('Unsupported Authorization type: [{0}, {1}]'.format(name, auth.type))

        self.__auths.update({name: (header, {key: cred})})

    def __call__(self, req):
        """
        """
        if not req._auths:
            return req

        for k, v in six.iteritems(req._auths):
            if not k in self.__auths:
                continue

            header, cred = self.__auths[k]
            req._p['header'].update(cred) if header else req.query.update(cred)

        return req


class BaseClient(object):
    """ base implementation of SwaggerClient """

    def __init__(self, auth=None):
        self.__auth = auth

    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = req_and_resp

        # handle options
        req._patch(opt)

        # apply authorizations
        if self.__auth:
            self.__auth.prepare(req) 

        return req, resp

