from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
from pyswagger.spec.v1_2.objects import (
    Info,
    Authorization,
    Scope,
    Items,
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
import six


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 

class PropertyTestCase(unittest.TestCase):
    """ make sure properties' existence & type """

    def test_resource_list(self):
        """ resource list """
        self.assertTrue(isinstance(app.raw.info, Info))
        self.assertEqual(app.raw.info.title, 'Swagger Sample App')
        self.assertEqual(app.raw.swaggerVersion, '1.2')

    def test_authorizations(self):
        """ authorizations """
        self.assertTrue('oauth2' in app.raw.authorizations)
        self.assertTrue(isinstance(app.raw.authorizations['oauth2'], Authorization))
        self.assertEqual(app.raw.authorizations['oauth2'].type, 'oauth2')

    def test_scope(self):
        """ scope """
        auth = app.raw.authorizations['oauth2']
        self.assertEqual(len(auth.scopes), 2)
        self.assertTrue(isinstance(auth.scopes[0], Scope))
        self.assertTrue(isinstance(auth.scopes[0], Scope))
        self.assertEqual(auth.scopes[0].scope, 'write:pets')
        self.assertEqual(auth.scopes[1].scope, 'read:pets')
        self.assertEqual(auth.scopes[1].description, 'Read your pets')

    def test_grant_type(self):
        """ grant type """
        auth = app.raw.authorizations['oauth2']
        self.assertTrue(isinstance(auth.grantTypes, GrantType))

    def test_implicit(self):
        """ implicit """
        grant = app.raw.authorizations['oauth2'].grantTypes
        self.assertTrue(isinstance(grant.implicit, Implicit))
        self.assertEqual(grant.implicit.tokenName, 'access_token')

    def test_login_endpoint(self):
        """ login endpoint """
        implicit = app.raw.authorizations['oauth2'].grantTypes.implicit
        self.assertTrue(isinstance(implicit.loginEndpoint, LoginEndpoint))
        self.assertEqual(implicit.loginEndpoint.url,
            'http://petstore.swagger.wordnik.com/api/oauth/dialog')
            

    def test_authorization_code(self):
        """ authorization code """
        grant = app.raw.authorizations['oauth2'].grantTypes
        self.assertTrue(isinstance(grant.authorization_code, AuthorizationCode))

    def test_token_request_endpoint(self):
        """ token request endpoint """
        auth = app.raw.authorizations['oauth2'].grantTypes.authorization_code
        self.assertTrue(isinstance(auth.tokenRequestEndpoint,TokenRequestEndpoint))
        self.assertEqual(auth.tokenRequestEndpoint.url,
            'http://petstore.swagger.wordnik.com/api/oauth/requestToken')
        self.assertEqual(auth.tokenRequestEndpoint.clientIdName, 'client_id')
        self.assertEqual(auth.tokenRequestEndpoint.clientSecretName, 'client_secret')

    def test_token_endpoint(self):
        """ token endpoint """
        auth = app.raw.authorizations['oauth2'].grantTypes.authorization_code
        self.assertTrue(isinstance(auth.tokenEndpoint, TokenEndpoint))
        self.assertEqual(auth.tokenEndpoint.url,
            'http://petstore.swagger.wordnik.com/api/oauth/token')
        self.assertEqual(auth.tokenEndpoint.tokenName, 'auth_code')

    def test_resource_pet(self):
        """ resource """
        pet = app.raw.apis['pet']
        self.assertTrue(isinstance(pet, Resource))
        self.assertEqual(pet.swaggerVersion, '1.2')
        self.assertEqual(pet.apiVersion, '1.0.0')
        self.assertEqual(pet.basePath, 'http://petstore.swagger.wordnik.com/api')
        self.assertEqual(pet.resourcePath, '/pet')
        self.assertTrue('application/json' in pet.produces)
        self.assertTrue('application/xml' in pet.produces)
        self.assertTrue('text/plain' in pet.produces)
        self.assertTrue('text/html' in pet.produces)

    def test_operation(self):
        """ operation """
        pet = app.raw.apis['pet']
        self.assertEqual(sorted(pet.apis.keys()), sorted([
            'updatePet',
            'addPet',
            'findPetsByStatus',
            'findPetsByTags',
            'partialUpdate',
            'updatePetWithForm',
            'deletePet',
            'getPetById',
            'uploadFile']
        ))

        updatePet = pet.apis['updatePet']
        self.assertTrue(isinstance(updatePet, Operation))
        self.assertEqual(updatePet.path, '/pet')
        self.assertEqual(updatePet.method, 'PUT')
        self.assertEqual(updatePet.summary, 'Update an existing pet')
        self.assertEqual(updatePet.notes, '')

    def test_parameter(self):
        """ parameter """
        p = app.raw.apis['pet'].apis['updatePet'].parameters[0]
        self.assertTrue(isinstance(p, Parameter))
        self.assertEqual(p.paramType, 'body')
        self.assertEqual(p.name, 'body')
        self.assertEqual(p.required, True)
        self.assertEqual(p.allowMultiple, False)
        self.assertEqual(p.description, 'Pet object that needs to be updated in the store')

    def test_response_message(self):
        """ response message """
        msg = app.raw.apis['pet'].apis['updatePet'].responseMessages[0]
        self.assertTrue(isinstance(msg, ResponseMessage))
        self.assertEqual(msg.code, 400)
        self.assertEqual(msg.message, 'Invalid ID supplied')

    def test_model(self):
        """ model """
        m = app.raw.apis['pet'].models['Pet']
        self.assertTrue(isinstance(m, Model))
        self.assertEqual(m.id, 'Pet');
        self.assertEqual(sorted(m.required), sorted(['id', 'name']))

    def test_authorization(self):
        """ authorization """
        auth = app.raw.apis['pet'].apis['partialUpdate'].authorizations['oauth2'][0]
        self.assertTrue(isinstance(auth, Authorizations))
        self.assertEqual(auth.scope, 'write:pets')

    def test_parent(self):
        """ make sure parent is assigned """
        self.assertTrue(app.raw.apis['pet'].models['Pet']._parent_ is app.raw.apis['pet'])
        self.assertTrue(app.raw.apis['user'].apis['getUserByName']._parent_ is app.raw.apis['user'])
        self.assertTrue(app.raw.info._parent_ is app.raw)


class DataTypeTestCase(unittest.TestCase):
    """ make sure data type ready """

    def test_operation(self):
        """ operation """ 
        op = app.raw.apis['pet'].apis['findPetsByStatus']
        self.assertEqual(op.type, 'array')
        self.assertEqual(getattr(op.items, '$ref'), 'Pet')

    def test_parameter(self):
        """ parameter """ 
        p = app.raw.apis['pet'].apis['findPetsByStatus'].parameters[0]
        self.assertTrue(isinstance(p, Parameter))
        self.assertEqual(p.required, True)
        self.assertEqual(p.defaultValue, 'available')
        self.assertEqual(p.type, 'string')
        self.assertTrue(isinstance(p.enum, list))
        self.assertEqual(sorted(p.enum), sorted(['available', 'pending', 'sold']))

    def test_property(self):
        """ property """ 
        p = app.raw.apis['pet'].models['Pet'].properties
        # id
        self.assertEqual(p['id'].type, 'integer')
        self.assertEqual(p['id'].format, 'int64')
        # we are not convert to real type here,
        # this case is handled by Upgrading from 1.2 to 2.0
        self.assertEqual(p['id'].minimum, '0.0')
        self.assertEqual(p['id'].maximum, '100.0')
        # category
        self.assertEqual(getattr(p['category'], '$ref'), 'Category')
        # name
        self.assertEqual(p['name'].type, 'string')
        # photoUrls
        self.assertEqual(p['photoUrls'].type, 'array')
        self.assertTrue(isinstance(p['photoUrls'].items, Items))
        self.assertEqual(p['photoUrls'].items.type, 'string')
        # tag
        self.assertEqual(p['tags'].type, 'array')
        self.assertTrue(isinstance(p['tags'].items, Items))
        self.assertEqual(getattr(p['tags'].items, '$ref'), 'Tag')
        # status
        self.assertEqual(p['status'].type, 'string')
        self.assertEqual(sorted(p['status'].enum), sorted(['available', 'pending', 'sold']))

    def test_field_name(self):
        """ field_name """
        self.assertEqual(sorted(app.raw._field_names_), sorted(['info', 'authorizations', 'apiVersion', 'swaggerVersion', 'apis']))

    def test_children(self):
        """ children """
        chd = app.raw._children_
        self.assertEqual(len(chd), 5)
        self.assertEqual(set(['apis/user', 'apis/pet', 'apis/store']), set([k for k, v in six.iteritems(chd) if isinstance(v, Resource)]))

