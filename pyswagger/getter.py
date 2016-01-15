from __future__ import absolute_import
from .consts import private
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
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        elif not isinstance(obj, six.string_types):
            raise ValueError('Unknown types: [{0}]'.format(str(type(obj))))

        # a very simple logic to distinguish json and yaml
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
        ret = None

        logger.info('to load: [{0}]'.format(path))

        # try to get extension from Getter.base_path
        _, ext = os.path.splitext(self.base_path)
        # try to get extension from path
        _, ext = os.path.splitext(path) if ext == '' else (None, ext)
        # .json is default extension to try
        ext = '.json' if ext == '' else ext
        # make sure we get .json or .yaml files
        if not path.endswith(ext):
            path = path + ext

        # trim the leading slash, which is invalid on Windows
        if os.name == 'nt' and path.startswith('/'):
            path = path[1:]

        logger.info('final path to load: [{0}]'.format(path))

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

