from __future__ import absolute_import
from .getter import UrlGetter, LocalGetter
from .spec.v1_2.parser import ResourceListContext
from .spec.v2_0.parser import SwaggerContext
from .scan import Scanner
from .scanner import TypeReduce
from .scanner.v1_2 import Upgrade
from .scanner.v2_0 import AssignParent, Resolve, PatchObject
from pyswagger import utils
import inspect
import base64
import six
import weakref


class SwaggerApp(object):
    """ Major component of pyswagger

    This object is tended to be used in read-only manner. Therefore,
    all accessible attributes are almost read-only properties.
    """

    sc_path = 1

    _shortcut_ = {
        sc_path: '#/paths'
    }

    def __init__(self):
        """ constructor
        """
        self.__root_url = None
        self.__root = None
        self.__raw = None
        self.__version = ''

        self.__op = None
        self.__m = None
        self.__url2obj = {}
        self.__schemes = []

        # TODO: allow init App-wised SCOPE_SEPARATOR

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

    @property
    def op(self):
        """ list of Operations, organized by utilsScopeDict

        :type: utils.ScopeDict of Operations
        """
        return self.__op

    @property
    def m(self):
        """ backward compatible, convert
        SwaggerApp.d to utils.ScopeDict
        """
        return self.__m

    @property
    def version(self):
        """
        """
        return self.__version

    @property
    def schemes(self):
        """
        """
        return self.__schemes

    @staticmethod
    def _prepare_url(url):
        """
        """
        getter = UrlGetter

        p = six.moves.urllib.parse.urlparse(url)
        if p.scheme == "":
            if p.netloc == "" and p.path != "":
                # it should be a file path
                getter = LocalGetter(p.path)
                url = utils.path2url(url)
            else:
                raise ValueError('url should be a http-url or file path -- ' + url)

        if inspect.isclass(getter):
            # default initialization is passing the url
            # you can override this behavior by passing an
            # initialized getter object.
            getter = getter(url)

        return getter, url, p.scheme

    def __load_json(self, url, getter=None, parser=None):
        """
        """
        if not getter:
            getter, url, _ = self._prepare_url(url)

        if url in self.__url2obj:
            # look into cache first
            return self.__url2obj[url]

        # get root document to check its swagger version.
        obj, _ = six.advance_iterator(getter)
        tmp = {'_tmp_': {}}
        if not parser:
            if utils.get_swagger_version(obj) == '1.2':
                # swagger 1.2
                with ResourceListContext(tmp, '_tmp_') as ctx:
                    ctx.parse(getter, obj)
            else:
                # swagger 2.0
                with SwaggerContext(tmp, '_tmp_') as ctx:
                    ctx.parse(obj)
        else:
            with parser(tmp, '_tmp_') as ctx:
                ctx.parse(obj)

        # update map of url to obj
        self.__url2obj.update({
            url: tmp['_tmp_']
        })

        return tmp['_tmp_']

    def __validate(self, url=None):
        """ check if this Swagger API valid or not.

        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: validation errors
        :rtype: list of tuple(where, type, msg).
        """
        v_mod = utils.import_string('.'.join([
            'pyswagger',
            'scanner',
            'v' + self.version.replace('.', '_'),
            'validate'
        ]))

        if not v_mod:
            # there is no validation module
            # for this version of spec
            return []

        s = Scanner(self)
        v = v_mod.Validate()

        if url:
            s.scan(route=[v], root=self.__url2obj[url])
        else:
            s.scan(route=[v], root=self.__raw)

        return v.errs

    def __prepare_obj(self, url):
        """
        """
        s = Scanner(self)
        self.__validate(url=url)

        obj = self.__url2obj[url]
        if self.version == '1.2':
            converter = Upgrade()
            s.scan(root=obj, route=[converter])
            obj = converter.swagger

            # We only have to run this scanner when upgrading from 1.2.
            # Mainly because we initial BaseObj via NullContext
            s.scan(root=obj, route=[AssignParent()])
        elif self.version == '2.0':
            pass
        else:
            raise NotImplementedError('Unsupported Version: {0}'.format(self.__version))

        # back to cache
        self.__url2obj[url] = obj 

        if url == self.__root_url:
            # TODO: ugly...
            self.__root = obj
            # update schemes if any
            if self.__root.schemes and len(self.__root.schemes) > 0:
                self.__schemes = self.__root.schemes

        s.scan(root=obj, route=[Resolve(), PatchObject()])

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
        local_getter, url, scheme = kls._prepare_url(url)
        getter = getter or local_getter
        app = kls()
        obj = app.__load_json(url, getter)

        setattr(app, '_' + kls.__name__ + '__root_url', url)
        setattr(app, '_' + kls.__name__ + '__version', utils.get_swagger_version(obj))
        setattr(app, '_' + kls.__name__ + '__raw', obj)
        app.schemes.append(scheme)

        return app

    def validate(self, strict=True):
        """ check if this Swagger API valid or not.

        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: validation errors
        :rtype: list of tuple(where, type, msg).
        """
        errs = self.__validate()
        if strict and len(errs):
            raise ValueError('this Swagger App contains error: {0}.'.format(len(errs)))

        return errs

    def prepare(self):
        """ preparation for loaded json
        """

        self.__prepare_obj(url=self.__root_url)
        self.__root = self.__url2obj[self.__root_url]

        s = Scanner(self)

        # reducer for Operation 
        tr = TypeReduce()
        s.scan(root=self.__root, route=[tr])

        # 'op' -- shortcut for Operation with tag and operaionId
        self.__op = utils.ScopeDict(tr.op)
        # 'm' -- shortcut for model in Swagger 1.2
        self.__m = utils.ScopeDict(self.__root.definitions)

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

    """ for backward compatible, for later version,
    please call SwaggerApp.create instead.
    """
    _create_ = create

    def resolve(self, path):
        """ reference resolver

        :param str path: a JSON Reference, refer to http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03 for details.
        :return: the referenced object, wrapped by weakref.ProxyType
        :rtype: weakref.ProxyType
        :raises ValueError: if path is not valid
        """
        if path == None or len(path) == 0:
            raise ValueError('Empty Path is not allowed')

        if not path.startswith('#'):
            raise ValueError('Invalid Path, root element should be \'#\', but [{0}]'.format(path))

        if path.endswith('/'):
            path = path[:-1]

        obj = self.root.resolve(utils.jp_split(path)[1:]) # heading element is #, mapping to self.root

        if obj == None:
            raise ValueError('Unable to resolve path, [{0}]'.format(path))

        if isinstance(obj, (six.string_types, int, list, dict)):
            return obj
        return weakref.proxy(obj)

    def s(self, p, b=_shortcut_[sc_path]):
        """ shortcut to access Objects
        """
        return self.resolve(utils.jp_compose('/' + p if not p.startswith('/') else p, base=b))


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
        if not req._security:
            return req

        for k, v in six.iteritems(req._security):
            if not k in self.__info:
                continue

            header, cred = self.__info[k]
            if header:
                req._p['header'].update(cred)
            else:
                utils.nv_tuple_list_replace(req._p['query'], utils.get_dict_as_tuple(cred))

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

    # TODO: comments
    __schemes__ = set()

    def __init__(self, security=None):
        """ constructor

        :param SwaggerSecurity security: the security holder
        """

        # placeholder of SwaggerSecurity
        self.__security = security

    def prepare_schemes(self, req):
        """
        """
        ret = self.__schemes__ & set(req.schemes)
        if len(ret) == 0:
            raise ValueError('No schemes available: {0}'.format(req.schemes))
        return ret

    def request(self, req_and_resp, opt):
        """ preprocess before performing a request, usually some patching.
        authorization also applied here.

        :param req_and_resp: tuple of SwaggerRequest and SwaggerResponse
        :type req_and_resp: (SwaggerRequest, SwaggerResponse)
        :return: patched request and response
        :rtype: SwaggerRequest, SwaggerResponse
        """
        req, resp = req_and_resp

        # apply authorizations
        if self.__security:
            self.__security(req) 

        return req, resp

