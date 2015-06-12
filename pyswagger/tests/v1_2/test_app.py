from pyswagger import SwaggerApp, errs, utils
from ..utils import get_test_data_folder
from pyswagger.spec.v2_0.objects import (
    Schema,
    Operation,
)
import unittest
import httpretty
import os
import six
import pytest
import sys


@pytest.mark.skipif(sys.version_info[:2] >= (3, 3), reason='httpretty corrupt in python3')
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
            'produces',
            '$ref',
            'responseMessages',
            'type',
            'uniqueItems',
            'summary',
            'notes'
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
            (('#/info', 'Info'), 'requirement description not meet.'),
            (('#/info', 'Info'), 'requirement title not meet.'),
            (('#/authorizations/oauth2', 'Authorization'), 'requirement type not meet.'),
            (('#/authorizations/oauth2/grantTypes/implicit/loginEndpoint', 'LoginEndpoint'), 'requirement url not meet.'),
            (('#/authorizations/oauth2/scopes/0', 'Scope'), 'requirement scope not meet.'),
            (('#/authorizations/oauth2/grantTypes/authorization_code/tokenRequestEndpoint', 'TokenRequestEndpoint'), 'requirement url not meet.'),
            (('#/apis/pet/apis/getPetById', 'Operation'), 'requirement method not meet.'),
            (('#/apis/pet/apis/getPetById/parameters/0', 'Parameter'), 'requirement name not meet.'),
            (('#/apis/pet/apis/getPetById/responseMessages/0', 'ResponseMessage'), 'requirement code not meet.'),
            (('#/apis/pet/apis', 'Operation'), 'requirement nickname not meet.'),
            (('#/apis/pet/models/Pet/properties/tags', 'Property'), 'array should be existed along with items'),
            (('#/apis/pet/apis/getPetById/parameters/0', 'Parameter'), 'allowMultiple should be applied on path, header, or query parameters'),
            (('#/apis/pet/apis/partialUpdate/parameters/1', 'Parameter'), 'body parameter with invalid name: qqq'),
            (('#/apis/pet/apis/partialUpdate/parameters/0', 'Parameter'), 'void is only allowed in Operation object.')
            ]))

    def test_raise_exception(self):
        """ raise exceptions in strict mode """
        self.assertRaises(errs.ValidationError, self.app.validate)


class SwaggerAppTestCase(unittest.TestCase):
    """ test case for SwaggerApp """

    def setUp(self):
        folder = get_test_data_folder(
            version='1.2',
        )

        def _hook(url):
            # a demo of hooking a remote url to local path
            p = six.moves.urllib.parse.urlparse(url)
            return utils.normalize_url(os.path.join(folder, p.path[1:]))

        self.app = SwaggerApp.load('http://petstore.io/wordnik', url_load_hook=_hook)
        self.app.prepare()

    def test_url(self):
        """ make sure url is not touched by hook """
        req, _ = self.app.op['getUserByName'](username='Tom')
        req.prepare()
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/user/Tom')

    def test_ref(self):
        """ test ref function """
        self.assertRaises(ValueError, self.app.resolve, None)
        self.assertRaises(ValueError, self.app.resolve, '')

        self.assertTrue(isinstance(self.app.resolve('#/definitions/user!##!User'), Schema))
        self.assertTrue(isinstance(self.app.resolve('#/paths/~1api~1user~1{username}/put'), Operation))
        self.assertEqual(self.app.resolve('#/paths/~1api~1store~1order/post/produces'), ['application/json'])
        self.assertEqual(self.app.resolve('#/host'), 'petstore.swagger.wordnik.com')

        # resolve with URL part
        # refer to 
        #      http://stackoverflow.com/questions/10246116/python-dereferencing-weakproxy 
        # for how to dereferencing weakref
        self.assertEqual(
            self.app.resolve('#/definitions/user!##!User').__repr__(),
            self.app.resolve('http://petstore.io/wordnik#/definitions/user!##!User').__repr__()
        )
        self.assertEqual(
           self.app.resolve('#/paths/~1api~1user~1{username}/put').__repr__(),
           self.app.resolve('http://petstore.io/wordnik#/paths/~1api~1user~1{username}/put').__repr__()
        )

    def test_scope_dict(self):
        """ ScopeDict is a syntactic suger
        to access scoped named object, ex. Operation, Model
        """
        # Operation
        self.assertTrue(self.app.op['user', 'getUserByName'], Operation)
        self.assertTrue(self.app.op['user', 'getUserByName'] is self.app.op['user!##!getUserByName'])
        self.assertTrue(self.app.op['getUserByName'] is self.app.op['user!##!getUserByName'])

    def test_shortcut(self):
        """ a short cut to Resource, Operation, Model from SwaggerApp """
        # Resource
        # TODO: resource is now replaced by tags
        #self.assertTrue(isinstance(app.rs['pet'], Resource))
        #self.assertTrue(isinstance(app.rs['user'], Resource))
        #self.assertTrue(isinstance(app.rs['store'], Resource))

        # Operation
        self.assertEqual(len(self.app.op.values()), 20)
        self.assertEqual(sorted(self.app.op.keys()), sorted([
            'pet!##!addPet',
            'pet!##!deletePet',
            'pet!##!findPetsByStatus',
            'pet!##!findPetsByTags',
            'pet!##!getPetById',
            'pet!##!partialUpdate',
            'pet!##!updatePet',
            'pet!##!updatePetWithForm',
            'pet!##!uploadFile',
            'store!##!deleteOrder',
            'store!##!getOrderById',
            'store!##!placeOrder',
            'user!##!createUser',
            'user!##!createUsersWithArrayInput',
            'user!##!createUsersWithListInput',
            'user!##!deleteUser',
            'user!##!getUserByName',
            'user!##!loginUser',
            'user!##!logoutUser',
            'user!##!updateUser'
        ]))
        self.assertTrue(self.app.op['user!##!getUserByName'], Operation)

        # Model
        d = self.app.resolve('#/definitions')
        self.assertEqual(len(d.values()), 5)
        self.assertEqual(sorted(d.keys()), sorted([
            'pet!##!Category',
            'pet!##!Pet',
            'pet!##!Tag',
            'store!##!Order',
            'user!##!User'
        ]))

