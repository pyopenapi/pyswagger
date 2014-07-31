from __future__ import absolute_import
from six.moves import urllib
from .getter import HttpGetter, FileGetter
from .parser import ResourceListContext
import inspect


class SwaggerApp(object):
    """ Resource Listing
    """
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

        # schema
        app = kls()
        setattr(app, '_schema_', tmp['_tmp_'])

        # resources
        for name, res in app._schema_.apis.iteritems():
            setattr(app, name, res)

        # TODO: model

        return app


class SwaggerClient(object):
    """
    Base Client Implementation
    """
    def __init__(self, *args, **kwargs):
        super(SwaggerClient, self).__init__()

    def __call__(self, ctx):
        raise NotImplementedError()

