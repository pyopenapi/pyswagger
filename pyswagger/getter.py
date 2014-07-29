from __future__ import absolute_import
from pyswagger import const
import json
import six

class Getter(object):
    """
    """

    def __init__(self, path):
        self.__base_path = path
        if self.__base_path.endswith('/'):
            self.__base_path = self.__base_path[:-1]
        self.__urls = [].append((path, ''))

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.__urls) == 0:
            raise StopIteration

        obj = self.load(self.__urls.pop(0))
        if isinstance(obj, six.string_types):
            obj = json.loads(obj)

        # find urls to retrieve
        if len(self.__urls) == 0:
            urls = self.__find_urls(obj)
            self.__urls.extend(zip(
                map(lambda u: self.__base_path + u, urls),
                map(lambda u: u[1:], urls)
            ))

        return obj

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
        if  const.SCHEMA_APIS in obj:
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
    def load(self, path):
        ret = None
        with open(path, 'r') as f:
            ret = f.read()

        return ret


class HttpGetter(Getter):
    """
    default getter implementation for remote resource file
    """
    def load(self, path):
        ret = None
        try:
            f = six.moves.urllib.urlopen(path)
            ret = f.read()

        finally:
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

