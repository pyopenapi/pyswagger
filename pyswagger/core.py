from __future__ import absolute_import
from six.moves import urllib
from .getter import HttpGetter, FileGetter
from .parser import ResourceListContext
from .scan import Scanner
from .scanner import Validate, TypeReduce, Resolve
from .utils import ScopeDict
import inspect


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

    @classmethod
    def _create_(kls, url, getter=None):
        """
        """

        local_getter = getter or HttpGetter
        p = urllib.parse.urlparse(url)
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
        s.scan(route=[Validate(), tr])

        # 'm' for model
        setattr(app, '_' + kls.__name__ + '__m', ScopeDict(tr.model))
        # 'op' for operation
        setattr(app, '_' + kls.__name__ + '__op', ScopeDict(tr.op))

        # resolve reference
        s.scan(route=[Resolve()])

        return app


class Client(object):
    """
    Base Client Implementation
    """
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__()

    def request(self, req, opt={}):
        raise NotImplementedError()

