from __future__ import absolute_import
from .consts import private
from .utils import patch_path
import json
import yaml
import six
import os
import logging


logger = logging.getLogger(__name__)


class Getter(six.Iterator):
    """ base of getter object

    Idealy, to subclass a getter, you just need to override load function.
    The part to extend getter would be finalized once Swagger 2.0 is ready.
    """

    def __init__(self, path):
        self.base_path = path

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.urls) == 0:
            raise StopIteration

        obj = self.load(self.urls.pop(0))

        # make sure data is string type
        if isinstance(obj, dict):
            pass
        elif isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        elif not isinstance(obj, six.string_types):
            raise ValueError('Unknown types: [{0}]'.format(str(type(obj))))

        # a very simple logic to distinguish json and yaml
        if isinstance(obj, six.string_types):
            try:
                if obj.startswith('{'):
                    obj = json.loads(obj)
                else:
                    obj = yaml.load(obj)
            except ValueError:
                raise Exception('Unknown format startswith {0} ...'.format(obj[:10]))

        return obj

    def load(self, path):
        """ load the resource, and return for parsing.

        :return: name and json object of resources
        :rtype: (str, dict)
        """
        raise NotImplementedError()

class LocalGetter(Getter):
    """ default getter implmenetation for local resource file
    """
    def __init__(self, path):
        super(LocalGetter, self).__init__(path)

        for n in private.SWAGGER_FILE_NAMES:
            if self.base_path.endswith(n):
                self.base_path = os.path.dirname(self.base_path)
                self.urls = [path]
                break
            else:
                p = os.path.join(path, n)
                if os.path.isfile(p):
                    self.urls = [p]
                    break
        else:
            # there is no file matched predefined file name:
            # - resource_list.json (1.2)
            # - swagger.json       (2.0)
            # in this case, we will locate them in this way:
            # - when 'path' points to a specific file, and its
            #   extension is either 'json' or 'yaml'.
            _, ext = os.path.splitext(path)
            for e in [private.FILE_EXT_JSON, private.FILE_EXT_YAML]:
                if ext.endswith(e):
                    self.base_path = os.path.dirname(path)
                    self.urls = [path]
                    break
            else:
                for e in [private.FILE_EXT_JSON, private.FILE_EXT_YAML]:
                    if os.path.isfile(path + '.' + e):
                        self.urls = [path + '.' + e]
                        break
                else:
                    raise ValueError('Unable to locate resource file: [{0}]'.format(path))

    def load(self, path):
        logger.info('to load: [{0}]'.format(path))

        path = patch_path(self.base_path, path)
        logger.info('final path to load: [{0}]'.format(path))

        ret = None
        with open(path, 'r') as f:
            ret = f.read()
        return ret


class UrlGetter(Getter):
    """ default getter implementation for remote resource file
    """
    def __init__(self, path):
        super(UrlGetter, self).__init__(path)
        if self.base_path.endswith('/'):
            self.base_path = self.base_path[:-1]
        self.urls = [path]

    def load(self, path):
        logger.info('to load: [{0}]'.format(path))

        ret = f = None
        try:
            f = six.moves.urllib.request.urlopen(path)
            ret = f.read()
        finally:
            if f:
                f.close()

        return ret


class DictGetter(Getter):
    """ a getter accept a dict as parameter without loading from file / url

    args:
     - urls: the urls to be loaded in upcoming resolving (the order should be matched to get result correct)
     - path2dict: a mapping from 'path' to 'dict', which is the mocking of 'downloaded data'
    """
    def __init__(self, urls, path2dict):
        super(DictGetter, self).__init__(urls[0])
        self.urls = urls
        self._path2dict = path2dict or {}

    def load(self, path):
        logger.info('to load: [{0}]'.format(path))

        return self._path2dict.get(path, {})

