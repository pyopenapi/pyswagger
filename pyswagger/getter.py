from __future__ import absolute_import
from pyswagger import const
import json
import six
import os


class Getter(six.Iterator):
    """
    """
    def __init__(self, path):
        self.base_path = path

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.urls) == 0:
            raise StopIteration

        path, name = self.urls.pop(0)
        obj = self.load(path)
        if isinstance(obj, six.string_types):
            obj = json.loads(obj)
        elif isinstance(obj, six.binary_type):
            obj = json.loads(obj.decode('utf-8'))
        else:
            raise ValueError('Unknown types: [{0}]'.format(str(type(obj))))

        # find urls to retrieve from resource listing file
        if name == '':
            urls = self.__find_urls(obj)
            # TODO: not worked in DictGetter
            self.urls.extend(zip(
                map(lambda u: self.base_path + u, urls),
                map(lambda u: u[1:], urls)
            ))

        return obj, name

    def load(self, path):
        """
        """
        raise NotImplementedError()

    def __find_urls(self, obj):
        """
        the only thing to do here is to find next resource-file to retrieve.
        to simplify implementation of getter, we need to maintain minimun
        knowledge of swagger schema.
        """
        urls = []
        if const.SCHEMA_APIS in obj:
            if isinstance(obj[const.SCHEMA_APIS], list):
                for api in obj[const.SCHEMA_APIS]:
                    urls.append(api[const.SCHEMA_PATH])
            else:
                raise TypeError('Invalid type of apis: ' + type(obj[const.SCHEMA_APIS]))

        return urls


class FileGetter(Getter):
    """
    default getter implmenetation for local resource file
    """
    def __init__(self, path):
        super(FileGetter, self).__init__(path)
        if self.base_path.endswith(const.RESOURCE_LISTING_FILE_NAME):
            self.base_path = os.path.dirname(self.base_path)
            self.urls = [(path, '')]
        else:
            self.urls = [(os.path.join(path, const.RESOURCE_LISTING_FILE_NAME), '')]

    def load(self, path):
        ret = None
        # make sure we get .json files
        if not path.endswith(const.RESOURCE_FILE_EXT):
            path = path + '.' + const.RESOURCE_FILE_EXT

        with open(path, 'r') as f:
            ret = f.read()

        return ret


class HttpGetter(Getter):
    """
    default getter implementation for remote resource file
    """
    def __init__(self, path):
        super(HttpGetter, self).__init__(path)
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


class DictGetter(Getter):
    """
    getter for resource in memory, need special initialization.
    """
    def __init__(self, path=None):
        super(DictGetter, self).__init__(path)

    def load(self, path):
        """
        """

    def upload(self, name, obj):
        """
        upload json object, could be either string or object.
        """

