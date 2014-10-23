from __future__ import absolute_import
from .getter import HttpGetter, FileGetter
from .spec.v1_2.parser import ResourceListContext
from .scan import Scanner
from .scanner import Validate, TypeReduce, Resolve, FixMinMax
from .utils import ScopeDict
import inspect
import base64
import six


class SwaggerApp(object):
    """ Major component of pyswagger

    This object is tended to be used in read-only manner. Therefore,
    all accessible attributes are almost read-only properties.
    """

    @property
    def root(self):
        """ schema representation of Swagger API, its structure may
        be different from different version of Swagger.

        There is 'schema' object in swagger 2.0, that's why I change this
        property name from 'schema' to 'root'.

        :type: pyswagger.obj.Swagger
        """
        return self.__schema

    # TODO: operationId is optional, we need another way to index operations.
    @property
    def op(self):
        """ list of Operations, organized by ScopeDict

        :type: ScopeDict of Operations
        """
        return self.__op

    # TODO: add member
    @property
    def d(self):
        """ dict of Definition Object

        :type: dict of Definition Object
        """
        return self.__m

    # TODO: add member
    @property
    def pd(self):
        """ dict of Parameter Definition Object

        :type: dict of Parameter Definition Object
        """

    # TODO: add member
    @property
    def rd(self):
        """ dict of Response Definition Object

        :type: dict of Response Definition Object
        """

    def validate(self, strict=True):
        """ check if this Swagger API valid or not.

        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: validation errors
        :rtype: list of tuple(where, type, msg).
        """
        s = Scanner(self)
        v = Validate()

        s.scan(route=[v])

        if strict and len(v.errs) > 0:
            raise ValueError('this Swagger App contains error: {0}.'.format(len(v.errs)))

        return v.errs

    @classmethod
    def _create_(kls, url, getter=None):
        """ factory of SwaggerApp

        :param str url: url of path of Swagger API definition
        :param getter: customized Getter
        :type getter: sub class/instance of Getter
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
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
        setattr(app, '_' + kls.__name__ + '__resrc', app.root.apis)

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
    """ authorization handler
    """

    def __init__(self, app):
        """ constructor

        :param SwaggerApp app: SwaggerApp
        """
        self.__app = app

        # placeholder of authorizations
        self.__auths = {}

    def update_with(self, name, auth_info):
        """ insert/clear authorizations

        :param str name: name of the authorization to be updated
        :param auth_info: the real authorization data, token, ...etc.
        :type auth_info: **(username, password)** for *basicAuth*, **token** in str for *oauth2*, *apiKey*.

        :raises ValueError: unsupported types of authorizations
        """
        auth = self.__app.root.authorizations.get(name, None)
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
        """ apply authorization for a request.

        :param SwaggerRequest req: the request to be authorized.
        :return: the updated request
        :rtype: SwaggerRequest
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
    """ base implementation of SwaggerClient, below is an minimum example
    to extend this class

    .. code-block:: python

        class MyClient(BaseClient):
            def request(self, req_and_resp, opt):
                # passing to parent for default patching behavior,
                # applying authorizations, ...etc.
                req, resp = super(MyClient, self).request(req_and_resp, opt)

                # perform request by req
                ...
                # apply result to resp
                resp.apply(header=header, raw=data_received, status=code)
                return resp
    """

    def __init__(self, auth=None):
        """ constructor

        :param SwaggerAuth auth: the authorization holder
        """

        # placeholder of SwaggerAuth
        self.__auth = auth

    def request(self, req_and_resp, opt={}):
        """ preprocess before performing a request, usually some patching.
        authorization also applied here.

        :param req_and_resp: tuple of SwaggerRequest and SwaggerResponse
        :type req_and_resp: (SwaggerRequest, SwaggerResponse)
        :return: patched request and response
        :rtype: SwaggerRequest, SwaggerResponse
        """
        req, resp = req_and_resp

        # handle options
        req._patch(opt)

        # apply authorizations
        if self.__auth:
            self.__auth.prepare(req) 

        return req, resp

