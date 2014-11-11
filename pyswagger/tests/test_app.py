from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.spec.v2_0.objects import (
    Schema,
    Operation,
)
import unittest
import httpretty
import os


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

        self.assertEqual(sorted(local_app.raw._field_names_), sorted(['info', 'authorizations', 'apiVersion', 'swaggerVersion', 'apis']))

        op = local_app.raw.apis['pet'].apis['updatePet']
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


class ValidationTestCase(unittest.TestCase):
    """ test case for validation """

    def setUp(self):
        self.app = SwaggerApp.load(get_test_data_folder(version='1.2', which='err'))

    def test_errs(self):
        """
        """
        errs = self.app.validate(strict=False)
        self.maxDiff = None
        self.assertEqual(sorted(errs), sorted([
            (('', 'Info'), 'requirement description not meet.'),
            (('', 'Info'), 'requirement title not meet.'),
            (('oauth2', 'Authorization'), 'requirement type not meet.'),
            (('oauth2', 'LoginEndpoint'), 'requirement url not meet.'),
            (('oauth2', 'Scope'), 'requirement scope not meet.'),
            (('oauth2', 'TokenRequestEndpoint'), 'requirement url not meet.'),
            (('pet!##!getPetById', 'Operation'), 'requirement method not meet.'),
            (('pet!##!getPetById', 'Parameter'), 'requirement name not meet.'),
            (('pet!##!getPetById', 'ResponseMessage'), 'requirement code not meet.'),
            (('pet', 'Operation'), 'requirement nickname not meet.'),
            (('pet!##!Pet!##!tags', 'Property'), 'array should be existed along with items'),
            (('pet!##!getPetById', 'Parameter'), 'allowMultiple should be applied on path, header, or query parameters'),
            (('pet!##!partialUpdate', 'Parameter'), 'body parameter with invalid name: qqq'),
            (('pet!##!partialUpdate', 'Parameter'), 'void is only allowed in Operation object.')
            ]))

    def test_raise_exception(self):
        """ raise exceptions in strict mode """
        self.assertRaises(ValueError, self.app.validate)


class SwaggerAppTestCase(unittest.TestCase):
    """ test case for SwaggerApp """

    def setUp(self):
        self.app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))

    def test_ref(self):
        """ test ref function """
        self.assertRaises(ValueError, self.app.ref, None)
        self.assertRaises(ValueError, self.app.ref, '')
        self.assertRaises(ValueError, self.app.ref, '//')

        self.assertTrue(isinstance(self.app.ref('#/definitions/user!##!User'), Schema))
        self.assertTrue(isinstance(self.app.ref('#/paths/~1user~1{username}/put'), Operation))
        self.assertEqual(self.app.ref('#/paths/~1store~1order/post/produces'), ['application/json'])
        self.assertEqual(self.app.ref('#/host'), 'petstore.swagger.wordnik.com')

