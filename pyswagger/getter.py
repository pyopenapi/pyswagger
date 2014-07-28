from __future__ import absolute_import
from pyswagger import const
import json

class Getter(object):
    """
    """

    def __init__(self, path):
        self.__base_path = path
        self.__urls = [].append(path)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.__urls) == 0:
            raise StopIteration

        obj = json.loads(self.load(self.__urls.pop(0)))

        # find urls to retrieve
        if len(self.__urls) == 0:
            urls = self.__find_urls(obj)
            self.__urls.extend(map(lambda u: self.__base_path + '/' + u, urls))

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



