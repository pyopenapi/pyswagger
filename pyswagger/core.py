from __future__ import absolute_import
from .getter import UrlGetter, LocalGetter
from .resolve import SwaggerResolver
from .primitives import SwaggerPrimitive, MimeCodec
from .spec.v1_2.parser import ResourceListContext
from .spec.v2_0.parser import SwaggerContext
from .spec.v2_0.objects import Operation
from .spec.base import BaseObj
from .scan import Scanner
from .scanner import TypeReduce, CycleDetector
from .scanner.v1_2 import Upgrade
from .scanner.v2_0 import AssignParent, Merge, Resolve, PatchObject, YamlFixer, Aggregate, NormalizeRef
from pyswagger import utils, errs, consts
import base64
import six
import weakref
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

    def __init__(self, url=None, url_load_hook=None, sep=consts.private.SCOPE_SEPARATOR, prim=None, mime_codec=None):
        """ constructor

        :param url str: url of swagger.json
        :param func url_load_hook: a way to redirect url to a accessible place. for self testing.
        :param sep str: separator used by pyswager.utils.ScopeDict
        :param prim pyswagger.primitives.SwaggerPrimitive: factory for primitives in Swagger.
        """

        logger.info('init with url: {0}'.format(url))

        self.__root = None
        self.__raw = None
        self.__version = ''

        self.__op = None
        self.__m = None
        self.__schemes = []
        self.__url=url

        # a map from json-reference to
        # - spec.BaseObj
        # - a map from json-pointer to spec.BaseObj
        self.__objs = {}
        self.__resolver = SwaggerResolver(url_load_hook)
        # keep a string reference to SwaggerApp when resolve
        self.__strong_refs = []

        # allow init App-wised SCOPE_SEPARATOR
        self.__sep = sep

        # init a default SwaggerPrimitive as factory for primitives
        self.__prim = prim if prim else SwaggerPrimitive()

        # MIME codec
        self.__mime_codec = mime_codec or MimeCodec()

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
    def prim_factory(self):
        """ primitive factory used by this app

        :type: pyswagger.primitives.SwaggerPrimitive
        """
        return self.__prim

    @property
    def mime_codec(self):
        """ mime codec used by this app

        :type: pyswagger.primitives.MimeCodec
        """
        return self.__mime_codec

    def load_obj(self, jref, getter=None, parser=None):
        """ load a object(those in spec._version_.objects) from a JSON reference.
        """
        obj = self.__resolver.resolve(jref, getter)

        # get root document to check its swagger version.
        tmp = {'_tmp_': {}}
        version = utils.get_swagger_version(obj)
        if version == '1.2':
            # swagger 1.2
            with ResourceListContext(tmp, '_tmp_') as ctx:
                ctx.parse(obj, jref, self.__resolver, getter)
        elif version == '2.0':
            # swagger 2.0
            with SwaggerContext(tmp, '_tmp_') as ctx:
                ctx.parse(obj)
        elif version == None and parser:
            with parser(tmp, '_tmp_') as ctx:
                ctx.parse(obj)

            version = tmp['_tmp_'].__swagger_version__ if hasattr(tmp['_tmp_'], '__swagger_version__') else version
        else:
            raise NotImplementedError('Unsupported Swagger Version: {0} from {1}'.format(version, jref))

        if not tmp['_tmp_']:
            raise Exception('Unable to parse object from {0}'.format(jref))

        logger.info('version: {0}'.format(version))

        return tmp['_tmp_'], version

    def prepare_obj(self, obj, jref):
        """ basic preparation of an object(those in sepc._version_.objects),
        and cache the 'prepared' object.
        """
        if not obj:
            raise Exception('unexpected, passing {0}:{1} to prepare'.format(obj, jref))

        s = Scanner(self)
        if self.version == '1.2':
            # upgrade from 1.2 to 2.0
            converter = Upgrade(self.__sep)
            s.scan(root=obj, route=[converter])
            obj = converter.swagger

            if not obj:
                raise Exception('unable to upgrade from 1.2: {0}'.format(jref))

            s.scan(root=obj, route=[AssignParent()])

        # normalize $ref
        url, jp = utils.jr_split(jref)
        s.scan(root=obj, route=[NormalizeRef(url)])
        # fix for yaml that treat response code as number
        s.scan(root=obj, route=[YamlFixer()], leaves=[Operation])

        # cache this object
        if url not in self.__objs:
            if jp == '#':
                self.__objs[url] = obj
            else:
                self.__objs[url] = {jp: obj}
        else:
            if not isinstance(self.__objs[url], dict):
                raise Exception('it should be able to resolve with BaseObj')
            self.__objs[url].update({jp: obj})

        # pre resolve Schema Object
        # note: make sure this object is cached before using 'Resolve' scanner
        s.scan(root=obj, route=[Resolve()])
        return obj

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

    @classmethod
    def load(kls, url, getter=None, parser=None, url_load_hook=None, sep=consts.private.SCOPE_SEPARATOR, prim=None, mime_codec=None):
        """ load json as a raw SwaggerApp

        :param str url: url of path of Swagger API definition
        :param getter: customized Getter
        :type getter: sub class/instance of Getter
        :param parser: the parser to parse the loaded json.
        :type parser: pyswagger.base.Context
        :param dict app_cache: the cache shared by related SwaggerApp
        :param func url_load_hook: hook to patch the url to load json
        :param str sep: scope-separater used in this SwaggerApp
        :param prim pyswager.primitives.SwaggerPrimitive: factory for primitives in Swagger
        :param mime_codec pyswagger.primitives.MimeCodec: MIME codec
        :return: the created SwaggerApp object
        :rtype: SwaggerApp
        :raises ValueError: if url is wrong
        :raises NotImplementedError: the swagger version is not supported.
        """

        logger.info('load with [{0}]'.format(url))

        url = utils.normalize_url(url)
        app = kls(url, url_load_hook=url_load_hook, sep=sep, prim=prim, mime_codec=mime_codec)
        app.__raw, app.__version = app.load_obj(url, getter=getter, parser=parser)
        if app.__version not in ['1.2', '2.0']:
            raise NotImplementedError('Unsupported Version: {0}'.format(self.__version))

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

        self.validate(strict=strict)
        self.__root = self.prepare_obj(self.raw, self.__url)

        if hasattr(self.__root, 'schemes') and self.__root.schemes:
            if len(self.__root.schemes) > 0:
                self.__schemes = self.__root.schemes
            else:
                # extract schemes from the url to load spec
                self.__schemes = [six.moves.urlparse(self.__url).schemes]

        s = Scanner(self)
        s.scan(root=self.__root, route=[Merge()])
        s.scan(root=self.__root, route=[PatchObject()])
        s.scan(root=self.__root, route=[Aggregate()])

        # reducer for Operation 
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

        obj = None
        url, jp = utils.jr_split(jref)
        if url:
            # check cacahed object against json reference by
            # comparing url first, and find those object prefixed with
            # the JSON pointer.
            o = self.__objs.get(url, None)
            if o:
                if isinstance(o, BaseObj):
                    obj = o.resolve(utils.jp_split(jp)[1:])
                elif isinstance(o, dict):
                    for k, v in six.iteritems(o):
                        if jp.startswith(k):
                            obj = v.resolve(utils.jp_split(jp[len(k):])[1:])
                            break
                else:
                    raise Exception('Unknown Cached Object: {0}'.format(str(type(o))))

            # this object is not loaded yet, load it
            if obj == None:
                obj, _ = self.load_obj(jref, parser=parser)
                if obj:
                    obj = self.prepare_obj(obj, jref)
        else:
            # a local reference, 'jref' is just a json-pointer
            if not jp.startswith('#'):
                raise ValueError('Invalid Path, root element should be \'#\', but [{0}]'.format(jref))

            obj = self.root.resolve(utils.jp_split(jp)[1:]) # heading element is #, mapping to self.root

        if obj == None:
            raise ValueError('Unable to resolve path, [{0}]'.format(jref))

        if isinstance(obj, (six.string_types, six.integer_types, list, dict)):
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

        # fix test bug when in python3 scheme, more details in commint msg
        ret = sorted(self.__schemes__ & set(req.schemes), reverse=True)

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

