from __future__ import absolute_import
from .getter import HttpGetter, FileGetter
from .spec.v1_2.parser import ResourceListContext
from .spec.v2_0.parser import SwaggerContext
from .scan import Scanner
from .scanner import TypeReduce, Resolve
from .scanner.v1_2 import FixMinMax, Upgrade
from .utils import ScopeDict, import_string
import inspect
import base64
import six


class SwaggerApp(object):
    """ Major component of pyswagger

    This object is tended to be used in read-only manner. Therefore,
    all accessible attributes are almost read-only properties.
    """
    def __init__(self):
        """ constructor
        """
        self.__root = None
        self.__raw = None
        self.__op = None
        self.__d = None
        self.__pd = None
        self.__rd = None
        self.__version = ''

    @property
    def root(self):
        # TODO: fix the comment
        """ schema representation of Swagger API, its structure may
        be different from different version of Swagger.

        There is 'schema' object in swagger 2.0, that's why I change this
        property name from 'schema' to 'root'.

        :type: pyswagger.obj.Swagger
        """
        return self.__root

    @property
    def raw(self):
        # TODO: fix the comment
        """ raw objects for original version of spec, indexed by
        version string.

        ex. to access raw objects representation of swagger 1.2, pass '1.2'
        as a key to this dict

        :type: dict
        """
        return self.__raw

    # TODO: operationId is optional, we need another way to index operations.
    @property
    def op(self):
        """ list of Operations, organized by ScopeDict

        :type: ScopeDict of Operations
        """
        return self.__op

    @property
    def m(self):
        """ backward compatible, refer to
        SwaggerApp.d for details
        """
        return self.d

    @property
    def d(self):
        """ dict of Definition Object

        :type: dict of Definition Object
        """
        # TODO: we didn't prepare d yet
        return self.__d

    @property
    def pd(self):
        """ dict of Parameter Definition Object

        :type: dict of Parameter Definition Object
        """
        # TODO: we didn't prepare pd yet
        return self.__pd

    @property
    def rd(self):
        """ dict of Response Definition Object

        :type: dict of Response Definition Object
        """
        # TODO: we didn't prepare rd yet
        return self.__rd

    @property
    def version(self):
        """
        """
        return self.__version

    @classmethod
    def load(kls, url, getter=None):
        """ load json as a raw SwaggerApp

        :param str url: url of path of Swagger API definition
        :param getter: customized Getter
        :type getter: sub class/instance of Getter
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
        :raises NotImplementedError: the swagger version is not supported.
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

        app = kls()
        tmp = {'_tmp_': {}}

        # get root document to check its swagger version.
        obj, _ = six.advance_iterator(local_getter)
        if 'swaggerVersion' in obj and obj['swaggerVersion'] == '1.2':
            # swagger 1.2
            with ResourceListContext(tmp, '_tmp_') as ctx:
                ctx.parse(local_getter, obj)

            setattr(app, '_' + kls.__name__ + '__version', '1.2')
        elif 'swagger' in obj:
            if obj['swagger'] == '2.0':
                # swagger 2.0
                with SwaggerContext(tmp, '_tmp_') as ctx:
                    ctx.parse(obj)

                setattr(app, '_' + kls.__name__ + '__version', '2.0')
            else:
                raise NotImplementedError('Unsupported Version: {0}'.format(obj['swagger']))
        else:
            raise LookupError('Unable to find swagger version')

        setattr(app, '_' + kls.__name__ + '__raw', tmp['_tmp_'])
        return app

    def validate(self, strict=True):
        """ check if this Swagger API valid or not.

        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: validation errors
        :rtype: list of tuple(where, type, msg).
        """
        v_mod = import_string('.'.join([
            'pyswagger',
            'scanner',
            'v' + self.version.replace('.', '_'),
            'validate'
        ]))

        if not v_mod:
            # there is no validation module
            # for this version of spec
            return

        s = Scanner(self)
        v = v_mod.Validate()

        s.scan(route=[v], root=self.__raw)

        if strict and len(v.errs) > 0:
            raise ValueError('this Swagger App contains error: {0}.'.format(len(v.errs)))

        return v.errs

    def prepare(self):
        """ preparation for loaded json
        """

        self.validate()

        s = Scanner(self)

        if self.version == '1.2':
            converter = Upgrade()
            s.scan(root=self.__raw, route=[converter])
            self.__root = converter.swagger
        elif self.version == '2.0':
            self.__root = self.__raw
        else:
            raise NotImplementedError('Unsupported Version: {0}'.format(self.__version))
       
        # TODO: need to change for 2.0
        # reducer for Operation & Model
        tr = TypeReduce()

        # TODO: this belongs to 1.2
        # convert types
        s.scan(root=self.__root, route=[FixMinMax(), tr])

        # 'm' for model
        self.__m = ScopeDict(tr.model)
        # 'op' for operation
        self.__op = ScopeDict(tr.op)

        # TODO: need to change for 2.0
        # resolve reference
        s.scan(root=self.__root, route=[Resolve()])

    @classmethod
    def _create_(kls, url, getter=None):
        """ for backward compatible, for later version,
        please call SwaggerApp.create instead.
        """
        return kls.create(url, getter)

    @classmethod
    def create(kls, url, getter=None):
        """ factory of SwaggerApp

        :param str url: url of path of Swagger API definition
        :param getter: customized Getter
        :type getter: sub class/instance of Getter
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
        :raises NotImplementedError: the swagger version is not supported.
        """

        app = kls.load(url, getter)
        app.prepare()

        return app


class SwaggerSecurity(object):
    """ security handler
    """

    def __init__(self, app):
        """ constructor

        :param SwaggerApp app: SwaggerApp
        """
        self.__app = app

        # placeholder of Security Info 
        self.__info = {}

    def update_with(self, name, security_info):
        """ insert/clear authorizations

        :param str name: name of the security info to be updated
        :param security_info: the real security data, token, ...etc.
        :type security_info: **(username, password)** for *basicAuth*, **token** in str for *oauth2*, *apiKey*.

        :raises ValueError: unsupported types of authorizations
        """
        s = self.__app.root.securityDefinitions.get(name, None)
        if s == None:
            raise ValueError('Unknown security name: [{0}]'.format(name))

        cred = security_info
        header = True
        if s.type == 'basic':
            cred = 'Basic ' + base64.standard_b64encode(six.b('{0}:{1}'.format(*security_info))).decode('utf-8')
            key = 'Authorization'
        elif s.type == 'apiKey':
            key = s.name
            header = getattr(s, 'in') == 'header'
        elif s.type == 'oauth2':
            key = 'access_token'
        else:
            raise ValueError('Unsupported Authorization type: [{0}, {1}]'.format(name, s.type))

        self.__info.update({name: (header, {key: cred})})

    def __call__(self, req):
        """ apply security info for a request.

        :param SwaggerRequest req: the request to be authorized.
        :return: the updated request
        :rtype: SwaggerRequest
        """
        if not req._auths:
            return req

        for k, v in six.iteritems(req._auths):
            if not k in self.__info:
                continue

            header, cred = self.__info[k]
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

    def __init__(self, security=None):
        """ constructor

        :param SwaggerSecurity security: the security holder
        """

        # placeholder of SwaggerSecurity
        self.__security = security

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

