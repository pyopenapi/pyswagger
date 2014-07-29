from __future__ import absolute_import
from six.moves import urllib
from .getter import HttpGetter, FileGetter
from .parse import ResourceListContext
import inspect


class SwaggerApp(object):
    """
    """
    def __init__(self, url, getter=None):
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
            local_getter = getter(url)

        ctx = ResourceListContext(getter)
        ctx.process()
        self.__set(ctx) 

    def __set(self, ctx):
        """
        """

    def __getattr__(self, name):
        

class SwaggerClient(object):
    """
    Base Client Implementation
    """
    def __init__(self, *args, **kwargs):
        super(SwaggerClient, self).__init__(*args, **kwargs)

    def __call__(self, ctx):
        raise NotImplementedError()

