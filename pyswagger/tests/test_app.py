from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.obj import (
    Resource
)
import unittest
import httpretty
import os


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))


class SwaggerAppTestCase(unittest.TestCase):
    """ test SwaggerApp utility function """

    def test_field_name(self):
        """ field_name """
        self.assertEqual(sorted(app.schema._field_names_), sorted(['info', 'authorizations', 'apiVersion', 'swaggerVersion', 'apis']))

    def test_field_rename(self):
        """ renamed field name """
        op = app.schema.apis['pet'].apis['updatePet']
        self.assertEqual(sorted(op._field_names_), sorted([
            'authorizations',
            'consumes',
            'defaultValue',
            'deprecated',
            'enum',
            'format',
            'items',
            'maximum',
            'method',
            'minimum',
            'nickname',
            'parameters',
            'path',
            'produces',
            'ref',
            'responseMessages',
            'type',
            'uniqueItems'
        ]))

    def test_children(self):
        """ children """
        chd = app.schema._children_
        self.assertEqual(len(chd), 5)
        self.assertEqual(set(['user', 'pet', 'store']), set([c[0] for c in chd if isinstance(c[1], Resource)]))


class HTTPGetterTestCase(unittest.TestCase):
    """ test HTTPGetter """

    @httpretty.activate
    def test_http_getter(self):
        """ make sure HTTPGetter works """

        folder = get_test_data_folder(version='1.2', which='wordnik')
        resource_list = user = pet = store = None

        with open(os.path.join(folder, 'resource_list.json')) as f:
            resource_list = f.read()

        with open(os.path.join(folder, 'user.json')) as f:
            user = f.read()

        with open(os.path.join(folder, 'pet.json')) as f:
            pet = f.read()

        with open(os.path.join(folder, 'store.json')) as f:
            store = f.read()

        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/api-docs',
            status=200,
            body=resource_list
            )

        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/api-docs/user',
            status=200,
            body=user
            )

        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/api-docs/pet',
            status=200,
            body=pet
            )

        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/api-docs/store',
            status=200,
            body=store
            )

        local_app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')

        self.assertEqual(sorted(local_app.schema._field_names_), sorted(['info', 'authorizations', 'apiVersion', 'swaggerVersion', 'apis']))

        op = local_app.schema.apis['pet'].apis['updatePet']
        self.assertEqual(sorted(op._field_names_), sorted([
            'authorizations',
            'consumes',
            'defaultValue',
            'deprecated',
            'enum',
            'format',
            'items',
            'maximum',
            'method',
            'minimum',
            'nickname',
            'parameters',
            'path',
            'produces',
            'ref',
            'responseMessages',
            'type',
            'uniqueItems'
        ]))

        chd = local_app.schema._children_
        self.assertEqual(len(chd), 5)
        self.assertEqual(set(['user', 'pet', 'store']), set([c[0] for c in chd if isinstance(c[1], Resource)]))

