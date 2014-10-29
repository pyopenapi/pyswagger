from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))


class Swagger_Upgrade_TestCase(unittest.TestCase):
    """ test for upgrade from converting 1.2 to 2.0 """

    def test_resource_list(self):
        """ ResourceList -> Swagger
        """
        s = app.root

        self.assertEqual(s.swagger, '2.0')
        self.assertEqual(s.host, 'petstore.swagger.wordnik.com')
        self.assertEqual(s.basePath, '/api')
        self.assertEqual(s.info.version, '1.0.0')
        self.assertEqual(s.schemes, ['http', 'https'])
        self.assertEqual(s.consumes, [])
        self.assertEqual(s.produces, [])

    def test_resource(self):
        """  Resource -> Tag, Operation
        make sure the way we rearrange resources
        to tags is correct.
        """
        s = app.root
        self.assertEqual(s.tags, ['store', 'user', 'pet'])

        p = app.root.paths
        self.assertEqual(sorted(p.keys()), sorted([
            '/user/createWithArray',
            '/store/order',
            '/user/login',
            '/user',
            '/pet',
            '/pet/findByTags',
            '/pet/findByStatus',
            '/store/order/{orderId}',
            '/user/logout',
            '/pet/uploadImage',
            '/user/createWithList',
            '/user/{username}',
            '/pet/{petId}'
        ]))

    def test_operation(self):
        """ Operation -> Operation
        """
        p = app.root.paths['/pet/{petId}']

        # getPetById
        o = p.get
        self.assertEqual(o.tags, ['pet'])
        self.assertEqual(o.operationId, 'getPetById')
        self.assertEqual(o.produces, ['application/json', 'application/xml', 'text/plain', 'text/html'])
        self.assertEqual(o.consumes, None)
        self.assertEqual(o.deprecated, False)

        # partialUpdate
        o = p.patch
        self.assertEqual(o.produces, ['application/json', 'application/xml'])
        self.assertEqual(o.consumes, ['application/json', 'application/xml'])
        self.assertEqual(o.security, {'oauth2': ['write:pets']})
        self.assertTrue('default' in o.responses)

        r = o.responses['default']
        self.assertEqual(r.headers, None)
        self.assertEqual(r.schema.type, 'array')
        self.assertEqual(getattr(r.schema.items, '$ref'), '#/definitions/Pet')

    def test_authorization(self):
        """ Authorization -> Security Scheme
        """
        s = app.root.securityDefinitions
        self.assertEqual(s.keys(), ['oauth2'])

        ss = s['oauth2']
        self.assertEqual(ss.type, 'oauth2')
        self.assertEqual(ss.name, None)
        self.assertEqual(getattr(ss, 'in'), None)
        self.assertEqual(ss.flow, 'accessCode')
        self.assertEqual(ss.authorizationUrl, 'http://petstore.swagger.wordnik.com/api/oauth/dialog')
        self.assertEqual(ss.tokenUrl, 'http://petstore.swagger.wordnik.com/api/oauth/token')
        self.assertEqual(ss.scopes, {'write:pets': '', 'read:pets': ''})

    def test_parameter(self):
        """ Parameter -> Parameter
        """

        # TODO: body
        o = app.root.paths['/pet/{petId}'].patch
        p = [p for p in o.parameters if getattr(p, 'in') == 'body'][0]
        self.assertEqual(getattr(p, 'in'), 'body')
        self.assertEqual(p.name, 'body')
        self.assertEqual(p.required, True)
        self.assertEqual(p.schema.type, 'Pet')

        # TODO: form

        # TODO: file


    def test_model(self):
        """ Model -> Definition
        """

