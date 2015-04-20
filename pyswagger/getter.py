from __future__ import absolute_import
from .consts import FILE_TYPE_JSON, FILE_TYPE_YAML, private
import json
import yaml
import six
import os

class Getter(six.Iterator):
    """ base of getter object

    Idealy, to subclass a getter, you just need to override load function.
    The part to extend getter would be finalized once Swagger 2.0 is ready.
    """

    def __init__(self, path, type_hint):
        self.base_path = path
        self.type_hint = type_hint

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.urls) == 0:
            raise StopIteration

        path, name = self.urls.pop(0)
        obj = self.load(path)

        # make sure data is string type
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        elif not isinstance(obj, six.string_types):
            raise ValueError('Unknown types: [{0}]'.format(str(type(obj))))

        if self.type_hint == FILE_TYPE_JSON:
            obj = json.loads(obj)
        elif self.type_hint == FILE_TYPE_YAML:
            obj = yaml.load(obj)

        # find urls to retrieve from resource listing file
        if name == '':
            urls = self.__find_urls(obj)
            self.urls.extend(zip(
                map(lambda u: self.base_path + u, urls),
                map(lambda u: u[1:], urls)
            ))

        return obj, name

    def load(self, path):
        """ load the resource, and return for parsing.

        :return: name and json object of resources
        :rtype: (str, dict)
        """
        raise NotImplementedError()

    def __find_urls(self, obj):
        """ helper function to located relative url in Resource Listing object.

        :param dict obj: json of Resource Listing object.
        :return: urls of resources
        :rtype: a list of str
        """
        urls = []
        if private.SCHEMA_APIS in obj:
            # This is a Swagger 1.2 spec, need to load subsequent resource files.
            if isinstance(obj[private.SCHEMA_APIS], list):
                for api in obj[private.SCHEMA_APIS]:
                    urls.append(api[private.SCHEMA_PATH])
            else:
                raise TypeError('Invalid type of apis: ' + type(obj[private.SCHEMA_APIS]))

        return urls


class LocalGetter(Getter):
    """ default getter implmenetation for local resource file
    """
    def __init__(self, path, type_hint):
        super(LocalGetter, self).__init__(path, type_hint)

        for n in private.SWAGGER_FILE_NAMES:
            if self.base_path.endswith(n):
                self.base_path = os.path.dirname(self.base_path)
                self.urls = [(path, '')]
                break
            else:
                p = os.path.join(path, n)
                if os.path.isfile(p):
                    self.urls = [(p, '')]
                    break
        else:
            raise ValueError('Unable to locate resource file: [{0}]'.format(path))

    def load(self, path):
        ret = None

        # make sure we get .json or .yaml files
        ext = private.EXT_MAPPING.get(self.type_hint, None)
        if ext and not path.endswith(ext):
            path = path + '.' + ext

        with open(path, 'r') as f:
            ret = f.read()
        return ret


class UrlGetter(Getter):
    """ default getter implementation for remote resource file
    """
    def __init__(self, path, type_hint):
        super(UrlGetter, self).__init__(path, type_hint)
        if self.base_path.endswith('/'):
            self.base_path = self.base_path[:-1]
        self.urls = [(path, '')]

    def load(self, path):
        ret = f = None
        try:
            f = six.moves.urllib.request.urlopen(path)
            ret = f.read()
        finally:
            if f:
                f.close()

        return ret

