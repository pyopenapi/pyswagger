from __future__ import absolute_import
from six.moves import urllib
from .getter import Getter
from .ctx import Context
import inspect


class File_Getter(Getter):
    """
    default getter implmenetation for local resource file
    """
    def load(self, path):
        ret = None
        with open(path, 'r') as f:
            ret = f.read()

        return ret


class HTTP_Getter(Getter):
    """
    default getter implementation for remote resource file
    """
    def load(self, path):
        ret = None
        try:
            f = urllib.urlopen(path)
            ret = f.read()

        finally:
            f.close()

        return ret


class App(object):
    """
    """
    def __init__(self, url, getter=None):
        """
        """

        local_getter = getter or HTTP_Getter
        p = urllib.parse.urlparse(url)
        if p.scheme == "":
            if p.netloc == "" and p.path != "":
                # it's a file path
                local_getter = File_Getter(p.path)
            else:
                raise ValueError('url should be a http-url or file path -- ' + url)

        if inspect.isclass(local_getter):
            # default initialization is passing the url
            # you can override this behavior by passing an
            # initialized getter object.
            local_getter = getter(url)

        # scan through resource list & resources
        with Context() as ctx:
            for obj in local_getter:
                self.__process(obj, ctx)

    def __process(self, obj, ctx):
        """
        """

