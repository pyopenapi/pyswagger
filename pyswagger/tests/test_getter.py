from pyswagger import App
from pyswagger.getter import UrlGetter, DictGetter, SimpleGetter
from pyswagger.resolve import Resolver
from pyswagger.utils import _diff_
from .utils import get_test_data_folder
import unittest
import os
import json


class _MyCustomException(Exception):
    pass

def _my_custom_load(path):
    raise _MyCustomException('a testing exception')

class _MyCustomGetter(SimpleGetter):
    __simple_getter_callback__ = _my_custom_load


class GetterTestCase(unittest.TestCase):
    """ test getter """

    def test_random_name_v2_0(self):
        """
        """
        path = get_test_data_folder(
            version='2.0',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')
        # should not raise ValueError
        app = App.create(path)

    def test_random_name_v1_2(self):
        """
        """
        path = get_test_data_folder(
            version='1.2',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')
        # should not raise ValueError
        app = App.create(path)

    def test_local_path_with_custome_getter(self):
        """ make sure path would be assigned when
        passing a getter class
        """
        cls = UrlGetter
        path = get_test_data_folder(
            version='2.0',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')

        # should not raise errors
        app = App.load(path, getter=cls)

    def test_dict_getter_v1_2(self):
        """ make sure 'DictGetter' works the same as 'LocalGetter'
        for Swagger 1.2
        """

        #
        # loading via DictGetter
        #
        path = get_test_data_folder(
            version='1.2',
            which='wordnik'
        )

        path_resource_list = os.path.join(path, 'resource_list.json')
        path_pet = os.path.join(path, 'pet.json')
        path_store = os.path.join(path, 'store.json')
        path_user = os.path.join(path, 'user.json')
        with open(path_resource_list, 'r') as f:
            resource_list = json.loads(f.read())
        with open(path_pet, 'r') as f:
            pet = json.loads(f.read())
        with open(path_store, 'r') as f:
            store = json.loads(f.read())
        with open(path_user, 'r') as f:
            user = json.loads(f.read())

        getter = DictGetter([
            path_resource_list,
            path_pet,
            path_user,
            path_store,
        ], {
            path_resource_list: resource_list,
            path_pet: pet,
            path_store: store,
            path_user: user,
        })
        app = App.load(path, resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), App.create(path).dump())), [])

        #
        # different path, mocking an url
        #
        getter = DictGetter([
            'http://petstore.com',
            'http://petstore.com/pet.json',
            'http://petstore.com/user.json',
            'http://petstore.com/store.json',
        ], {
            'http://petstore.com': resource_list,
            'http://petstore.com/pet.json': pet,
            'http://petstore.com/store.json': store,
            'http://petstore.com/user.json': user
        })
        app = App.load('http://petstore.com', resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), App.create(path).dump(), exclude=['$ref'])), [])

        #
        # provide empty path
        #
        getter = DictGetter([
            '',
            'pet.json',
            'user.json',
            'store.json',
        ], {
            '': resource_list,
            'pet.json': pet,
            'store.json': store,
            'user.json': user
        })
        app = App.load('http://petstore.com', resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), App.create(path).dump(), exclude=['$ref'])), [])


    def test_dict_getter_v2_0(self):
        """ make sure 'DictGetter' works the same as 'LocalGetter'
        for Swagger 2.0
        """

        #
        # loading via DictGetter
        #
        path = get_test_data_folder(
            version='2.0',
            which='wordnik'
        )

        origin_app = App.create(path)

        with open(os.path.join(path, 'swagger.json'), 'r') as f:
            spec = json.loads(f.read())

        getter = DictGetter([path], {
            os.path.join(path, 'swagger.json'): spec
        })
        app = App.load(path, resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), origin_app.dump())), [])

        #
        # loading via wrong path, should be ok when all internal $ref are not absoluted
        #
        getter = DictGetter([''], {
            '': spec
        })
        app = App.load('', resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), origin_app.dump(), exclude=['$ref'])), [])

        #
        # faking http path
        #
        getter = DictGetter(['https://petstore.com'], {
            'https://petstore.com': spec
        })
        app = App.load('https://petstore.com', resolver=Resolver(default_getter=getter))
        app.prepare()

        # make sure it produce the same App in default way
        self.assertEqual(sorted(_diff_(app.dump(), origin_app.dump(), exclude=['$ref'])), [])

    def test_simple_getter_callback(self):
        """ make sure __simple_getter_callback__ is called """

        path = get_test_data_folder(
            version='2.0',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')

        # should raise some specific error
        self.assertRaises(_MyCustomException, App.load, path, getter=_MyCustomGetter)

