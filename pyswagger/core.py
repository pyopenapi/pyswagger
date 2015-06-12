from __future__ import absolute_import
from .getter import UrlGetter, LocalGetter
from .spec.v1_2.parser import ResourceListContext
from .spec.v2_0.parser import SwaggerContext
from .spec.v2_0.objects import Operation
from .scan import Scanner
from .scanner import TypeReduce, CycleDetector
from .scanner.v1_2 import Upgrade
from .scanner.v2_0 import AssignParent, Resolve, PatchObject, YamlFixer
from pyswagger import utils, errs, consts
import inspect
import base64
import six
import weakref
import os
import logging


logger = logging.getLogger(__name__)


class SwaggerApp(object):
    """ Major component of pyswagger

    This object is tended to be used in read-only manner. Therefore,
    all accessible attributes are almost read-only properties.
    """

    sc_path = 1

    _shortcut_ = {
        sc_path: ('/', '#/paths')
    }

    def __init__(self, url=None, app_cache=None, url_load_hook=None, sep=consts.private.SCOPE_SEPARATOR):
        """ constructor

        :param url str: url of swagger.json
        :param dict app_cache: a url map shared by SwaggerApp(s), mapping from url to SwaggerApp
        :param func url_load_hook: a way to redirect url to a accessible place. for self testing.
        """

        logger.info('init with url: {0}'.format(url))

        self.__root = None
        self.__raw = None
        self.__version = ''

        self.__op = None
        self.__m = None
        self.__schemes = []
        self.__url=url

        # a map from url to SwaggerApp
        self.__app_cache = {} if app_cache == None else app_cache
        # keep a string reference to SwaggerApp when resolve
        self.__strong_refs = []

        # things to make unittest easier,
        # all urls to load json would go through this hook
        self.__url_load_hook = url_load_hook

        # allow init App-wised SCOPE_SEPARATOR
        self.__sep = sep

    @property
    def root(self):
        """ schema representation of Swagger API, its structure may
        be different from different version of Swagger.

        There is 'Schema' object in swagger 2.0, that's why I change this
        property name from 'schema' to 'root'.

        :type: pyswagger.spec.v2_0.objects.Swagger
        """
        return self.__root

    @property
    def raw(self):
        """ raw objects for original version of loaded resources.
        When loaded json is the latest version we supported, this property is the same as SwaggerApp.root

        :type: ex. when loading Swagger 1.2, the type is pyswagger.spec.v1_2.objects.ResourceList
        """
        return self.__raw

    @property
    def op(self):
        """ list of Operations, organized by utils.ScopeDict

        In Swagger 2.0, Operation(s) can be organized with Tags and Operation.operationId.
        ex. if there is an operation with tag:['user', 'security'] and operationId:get_one,
        here is the combination of keys to access it:
        - .op['user', 'get_one']
        - .op['security', 'get_one']
        - .op['get_one']

        :type: pyswagger.utils.ScopeDict of pyswagger.spec.v2_0.objects.Operation
        """
        return self.__op

    @property
    def m(self):
        """ backward compatible to access Swagger.definitions in Swagger 2.0,
        and Resource.Model in Swagger 1.2.

        ex. a Model:user in Resource:Users, access it by .m['Users', 'user'].
        For Schema object in Swagger 2.0, just access it by it key in json.

        :type: pyswagger.utils.ScopeDict
        """
        return self.__m

    @property
    def version(self):
        """ original version of loaded json

        :type: str
        """
        return self.__version

    @property
    def schemes(self):
        """ supported schemes, refer to Swagger.schemes in Swagger 2.0 for details

        :type: list of str, ex. ['http', 'https']
        """
        return self.__schemes

    @property
    def url(self):
        """
        """
        return self.__url

    @property
    def _app_cache(self):
        """ internal usage
        """
        return self.__app_cache

    def _load_obj(self, url, getter=None, parser=None):
        """
        """
        if url in self.__app_cache:
            logger.info('{0} hit cache'.format(url))

            # look into cache first
            return

        if not getter:
            # apply hook when use this url to load
            # note that we didn't cache SwaggerApp with this local_url

            local_url = url if not self.__url_load_hook else self.__url_load_hook(url)

            logger.info('{0} patch to {1}'.format(url, local_url))

            getter = UrlGetter
            p = six.moves.urllib.parse.urlparse(local_url)
            if p.scheme == 'file' and p.path:
                getter = LocalGetter(os.path.join(p.netloc, p.path))

        if inspect.isclass(getter):
            # default initialization is passing the url
            # you can override this behavior by passing an
            # initialized getter object.
            getter = getter(local_url)

        # get root document to check its swagger version.
        obj, _ = six.advance_iterator(getter)
        tmp = {'_tmp_': {}}
        version = utils.get_swagger_version(obj)
        if version == '1.2':
            # swagger 1.2
            with ResourceListContext(tmp, '_tmp_') as ctx:
                ctx.parse(getter, obj)
        elif version == '2.0':
            # swagger 2.0
            with SwaggerContext(tmp, '_tmp_') as ctx:
                ctx.parse(obj)
        elif version == None and parser:
            with parser(tmp, '_tmp_') as ctx:
                ctx.parse(obj)

            version = tmp['_tmp_'].__swagger_version__ if hasattr(tmp['_tmp_'], '__swagger_version__') else version
        else:
            raise NotImplementedError('Unsupported Swagger Version: {0} from {1}'.format(version, url))

        logger.info('version: {0}'.format(version))

        self.__app_cache[url] = weakref.proxy(self) # avoid circular reference
        self.__version = version
        self.__raw = tmp['_tmp_']

    def _validate(self):
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

        s.scan(route=[v], root=self.__raw)
        return v.errs

    def _prepare_obj(self, strict=True):
        """
        """
        if self.__root:
            return

        s = Scanner(self)
        self.validate(strict=strict)

        if self.version == '1.2':
            converter = Upgrade(self.__sep)
            s.scan(root=self.raw, route=[converter])
            obj = converter.swagger

            # We only have to run this scanner when upgrading from 1.2.
            # Mainly because we initial BaseObj via NullContext
            s.scan(root=obj, route=[AssignParent()])

            self.__root = obj
        elif self.version == '2.0':
            s.scan(root=self.raw, route=[YamlFixer()], leaves=[Operation])
            self.__root = self.raw
        else:
            raise NotImplementedError('Unsupported Version: {0}'.format(self.__version))

        if hasattr(self.__root, 'schemes') and self.__root.schemes:
            if len(self.__root.schemes) > 0:
                self.__schemes = self.__root.schemes

        s.scan(root=self.__root, route=[Resolve()])
        s.scan(root=self.__root, route=[PatchObject()])

    @classmethod
    def load(kls, url, getter=None, parser=None, app_cache=None, url_load_hook=None, sep=consts.private.SCOPE_SEPARATOR):
        """ load json as a raw SwaggerApp

        :param str url: url of path of Swagger API definition
        :param getter: customized Getter
        :type getter: sub class/instance of Getter
        :param parser: the parser to parse the loaded json.
        :type parser: pyswagger.base.Context
        :param dict app_cache: the cache shared by related SwaggerApp
        :param func url_load_hook: hook to patch the url to load json
        :param str sep: scope-separater used in this SwaggerApp
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
        :raises NotImplementedError: the swagger version is not supported.
        """

        logger.info('load with [{0}]'.format(url))

        url = utils.normalize_url(url)
        app = kls(url, app_cache=app_cache, url_load_hook=url_load_hook, sep=sep)

        app._load_obj(url, getter, parser)

        # update schem if any
        p = six.moves.urllib.parse.urlparse(url)
        if p.scheme:
            app.schemes.append(p.scheme)

        return app

    def validate(self, strict=True):
        """ check if this Swagger API valid or not.

        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: validation errors
        :rtype: list of tuple(where, type, msg).
        """

        result = self._validate()
        if strict and len(result):
            raise errs.ValidationError('this Swagger App contains error: {0}.'.format(len(result)))

        return result

    def prepare(self, strict=True):
        """ preparation for loaded json

        :param bool strict: when in strict mode, exception would be raised if not valid.
        """

        self._prepare_obj(strict=strict)

        # reducer for Operation 
        s = Scanner(self)
        tr = TypeReduce(self.__sep)
        cy = CycleDetector()
        s.scan(root=self.__root, route=[tr, cy])

        # 'op' -- shortcut for Operation with tag and operaionId
        self.__op = utils.ScopeDict(tr.op)
        # 'm' -- shortcut for model in Swagger 1.2
        if hasattr(self.__root, 'definitions') and self.__root.definitions != None:
            self.__m = utils.ScopeDict(self.__root.definitions)
        else:
            self.__m = utils.ScopeDict({})
        # update scope-separater
        self.__m.sep = self.__sep
        self.__op.sep = self.__sep

        # cycle detection
        if len(cy.cycles['schema']) > 0 and strict:
            raise errs.CycleDetectionError('Cycles detected in Schema Object: {0}'.format(cy.cycles['schema']))

    @classmethod
    def create(kls, url, strict=True):
        """ factory of SwaggerApp

        :param str url: url of path of Swagger API definition
        :param bool strict: when in strict mode, exception would be raised if not valid.
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
        :raises NotImplementedError: the swagger version is not supported.
        """
        app = kls.load(url)
        app.prepare(strict=strict)

        return app

    """ for backward compatible, for later version,
    please call SwaggerApp.create instead.
    """
    _create_ = create

    def resolve(self, jref, parser=None):
        """ JSON reference resolver

        :param str jref: a JSON Reference, refer to http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03 for details.
        :param parser: the parser corresponding to target object.
        :type parser: pyswagger.base.Context
        :return: the referenced object, wrapped by weakref.ProxyType
        :rtype: weakref.ProxyType
        :raises ValueError: if path is not valid
        """

        logger.info('resolving: [{0}]'.format(jref))

        if jref == None or len(jref) == 0:
            raise ValueError('Empty Path is not allowed')

        url, jp = utils.jr_split(jref)
        if url:
            if url not in self.__app_cache:
                # This loaded SwaggerApp would be kept in app_cache.
                app = SwaggerApp.load(url, parser=parser, app_cache=self.__app_cache, url_load_hook=self.__url_load_hook)
                app.prepare()

                # nothing but only keeping a strong reference of
                # loaded SwaggerApp.
                self.__strong_refs.append(app)

            return self.__app_cache[url].resolve(jp)

        if not jp.startswith('#'):
            raise ValueError('Invalid Path, root element should be \'#\', but [{0}]'.format(jref))

        obj = self.root.resolve(utils.jp_split(jp)[1:]) # heading element is #, mapping to self.root

        if obj == None:
            raise ValueError('Unable to resolve path, [{0}]'.format(jref))

        if isinstance(obj, (six.string_types, int, list, dict)):
            return obj
        return weakref.proxy(obj)

    def s(self, p, b=_shortcut_[sc_path]):
        """ shortcut of SwaggerApp.resolve.
        We provide a default base for '#/paths'. ex. to access '#/paths/~1user/get',
        just call SwaggerApp.s('user/get')

        :param str p: path relative to base
        :param tuple b: a tuple (expected_prefix, base) to represent a 'base'
        """

        if b[0]:
            return self.resolve(utils.jp_compose(b[0] + p if not p.startswith(b[0]) else p, base=b[1]))
        else:
            return self.resolve(utils.jp_compose(p, base=b[1]))

    def dump(self):
        """ dump into Swagger Document

        :rtype: dict
        :return: dict representation of Swagger
        """
        return self.root.dump()



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

        for s in req._security:
            for k, v in six.iteritems(s):
                if not k in self.__info:
                    logger.info('missing: [{0}]'.format(k))
                    continue

                logger.info('applying: [{0}]'.format(k))

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

            # declare supported schemes here
            __schemes__ = ['http', 'https']

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

    # supported schemes, ex. ['http', 'https', 'ws', 'ftp']
    __schemes__ = set()

    def __init__(self, security=None):
        """ constructor

        :param SwaggerSecurity security: the security holder
        """

        # placeholder of SwaggerSecurity
        self.__security = security

    def prepare_schemes(self, req):
        """ make sure this client support schemes required by current request

        :param pyswagger.io.SwaggerRequest req: current request object
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

        # dump info for debugging
        logger.info('request.url: {0}'.format(req.url))
        logger.info('request.header: {0}'.format(req.header))
        logger.info('request.query: {0}'.format(req.query))
        logger.info('request.file: {0}'.format(req.files))
        logger.info('request.schemes: {0}'.format(req.schemes))

        # apply authorizations
        if self.__security:
            self.__security(req) 

        return req, resp

