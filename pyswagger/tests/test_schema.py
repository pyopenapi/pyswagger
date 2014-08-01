from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.obj import (
    Info,
    Authorization,
    Scope,
    GrantType,
    Implicit,
    AuthorizationCode,
    LoginEndpoint,
    TokenRequestEndpoint,
    TokenEndpoint,
    Resource,
    Operation,
    Parameter,
    ResponseMessage,
    Authorizations,
    Model)
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 

class PropertyTestCase(unittest.TestCase):
    """ make sure properties' existence & type """

    def test_resource_list(self):
        """ resource list """
        self.assertTrue(isinstance(app._schema_.info, Info))
        self.assertEqual(app._schema_.info.title, 'Swagger Sample App')
        self.assertEqual(app._schema_.swaggerVersion, '1.2')
        # description is ignored 
        self.assertRaises(AttributeError, getattr, app._schema_.info, 'description')

    def test_authorizations(self):
        """ authorizations """
        self.assertIn('oauth2', app._schema_.authorizations)
        self.assertTrue(isinstance(app._schema_.authorizations['oauth2'], Authorization))
        self.assertEqual(app._schema_.authorizations['oauth2'].type, 'oauth2')

    def test_scope(self):
        """ scope """
        auth = app._schema_.authorizations['oauth2']
        self.assertEqual(len(auth.scopes), 2)
        self.assertTrue(isinstance(auth.scopes[0], Scope))
        self.assertTrue(isinstance(auth.scopes[0], Scope))
        self.assertEqual(auth.scopes[0].scope, 'write:pets')
        self.assertEqual(auth.scopes[1].scope, 'read:pets')
        self.assertRaises(AttributeError, getattr, auth.scopes[1], 'description')

    def test_grant_type(self):
        """ grant type """
        auth = app._schema_.authorizations['oauth2']
        self.assertTrue(isinstance(auth.grantTypes, GrantType))

    def test_implicit(self):
        """ implicit """
        grant = app._schema_.authorizations['oauth2'].grantTypes
        self.assertTrue(isinstance(grant.implicit, Implicit))
        self.assertEqual(grant.implicit.tokenName, 'access_token')

    def test_login_endpoint(self):
        """ login endpoint """
        implicit = app._schema_.authorizations['oauth2'].grantTypes.implicit
        self.assertTrue(isinstance(implicit.loginEndpoint, LoginEndpoint))
        self.assertEqual(implicit.loginEndpoint.url,
            'http://petstore.swagger.wordnik.com/oauth/dialog')

    def test_authorization_code(self):
        """ authorization code """
        grant = app._schema_.authorizations['oauth2'].grantTypes
        self.assertTrue(isinstance(grant.authorization_code, AuthorizationCode))

    def test_token_request_endpoint(self):
        """ token request endpoint """
        auth = app._schema_.authorizations['oauth2'].grantTypes.authorization_code
        self.assertTrue(isinstance(auth.tokenRequestEndpoint,TokenRequestEndpoint))
        self.assertEqual(auth.tokenRequestEndpoint.url,
            'http://petstore.swagger.wordnik.com/oauth/requestToken')
        self.assertEqual(auth.tokenRequestEndpoint.clientIdName, 'client_id')
        self.assertEqual(auth.tokenRequestEndpoint.clientSecretName, 'client_secret')

    def test_token_endpoint(self):
        """ token endpoint """
        auth = app._schema_.authorizations['oauth2'].grantTypes.authorization_code
        self.assertTrue(isinstance(auth.tokenEndpoint, TokenEndpoint))
        self.assertEqual(auth.tokenEndpoint.url,
            'http://petstore.swagger.wordnik.com/oauth/token')
        self.assertEqual(auth.tokenEndpoint.tokenName, 'auth_code')

    def test_resource_pet(self):
        """ resource """
        pet = app._schema_.apis['pet']
        self.assertTrue(isinstance(pet, Resource))
        self.assertEqual(pet.swaggerVersion, '1.2')
        self.assertEqual(pet.apiVersion, '1.0.0')
        self.assertEqual(pet.basePath, 'http://petstore.swagger.wordnik.com/api')
        self.assertEqual(pet.resourcePath, '/pet')
        self.assertIn('application/json', pet.produces)
        self.assertIn('application/xml', pet.produces)
        self.assertIn('text/plain', pet.produces)
        self.assertIn('text/html', pet.produces)

    def test_operation(self):
        """ operation """
        pet = app._schema_.apis['pet']
        self.assertItemsEqual(pet.apis.keys(), (
            'updatePet',
            'addPet',
            'findPetsByStatus',
            'findPetsByTags',
            'partialUpdate',
            'updatePetWithForm',
            'deletePet',
            'getPetById',
            'uploadFile'
        ))

        updatePet = pet.apis['updatePet']
        self.assertTrue(isinstance(updatePet, Operation))
        self.assertEqual(updatePet.path, '/pet')
        self.assertEqual(updatePet.method, 'PUT')
        self.assertRaises(AttributeError, getattr, updatePet, 'summary')
        self.assertRaises(AttributeError, getattr, updatePet, 'note')

    def test_parameter(self):
        """ parameter """
        p = app._schema_.apis['pet'].apis['updatePet'].parameters[0]
        self.assertTrue(isinstance(p, Parameter))
        self.assertEqual(p.paramType, 'body')
        self.assertEqual(p.name, 'body')
        self.assertEqual(p.required, True)
        self.assertEqual(p.allowMultiple, False)
        self.assertRaises(AttributeError, getattr, p, 'description')

    def test_response_message(self):
        """ response message """
        msg = app._schema_.apis['pet'].apis['updatePet'].responseMessages[0]
        self.assertTrue(isinstance(msg, ResponseMessage))
        self.assertEqual(msg.code, 400)
        self.assertEqual(msg.message, 'Invalid ID supplied')

    def test_model(self):
        """ model """
        m = app._schema_.apis['pet'].models['Pet']
        self.assertTrue(isinstance(m, Model))
        self.assertEqual(m.id, 'Pet');
        self.assertItemsEqual(m.required, ['id', 'name'])

    def test_authorization(self):
        """ authorization """
        auth = app._schema_.apis['pet'].apis['partialUpdate'].authorizations['oauth2'][0]
        self.assertTrue(isinstance(auth, Authorizations))
        self.assertEqual(auth.scope, 'write:pets')

    def test_shortcut(self):
        """ a short cut to Resource from SwaggerApp """
        self.assertTrue(isinstance(app.pet, Resource))
        self.assertTrue(isinstance(app.user, Resource))
        self.assertTrue(isinstance(app.store, Resource))

