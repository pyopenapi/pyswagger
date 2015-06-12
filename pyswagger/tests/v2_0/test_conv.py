from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
from ...utils import _diff_
import os
import json
import unittest


class ConverterTestCase(unittest.TestCase):
    """ test for converter """

    def test_v2_0(self):
        """ convert from 2.0 to 2.0 """
        path = get_test_data_folder(version='2.0', which='wordnik')
        app = SwaggerApp.create(path)

        # load swagger.json into dict
        origin = None
        with open(os.path.join(path, 'swagger.json')) as r:
            origin = json.loads(r.read())

        # diff for empty list or dict is allowed
        self.assertEqual(sorted(_diff_(origin, app.dump())), sorted([
            ('paths/~1pet~1{petId}/get/security/0/api_key', "list", "NoneType"),
            ('paths/~1store~1inventory/get/parameters', None, None),
            ('paths/~1store~1inventory/get/security/0/api_key', "list", "NoneType"),
            ('paths/~1user~1logout/get/parameters', None, None)
        ]))
            

class Converter_v1_2_TestCase(unittest.TestCase):
    """ test for convert from 1.2
    
        Not converted:
        - Response Message Object
        - Token Request Endpoint Object
        - API Object
        - Resource Object
    """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.load(get_test_data_folder(
            version='1.2', which='wordnik'), sep=':'
        )
        kls.app.prepare()

        with open('./test.json', 'w') as r:
            r.write(json.dumps(kls.app.dump(), indent=3))

    def test_items(self):
        """
        """
        # $ref
        expect = {
            '$ref':'#/definitions/pet:Pet'
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/{petId}').patch.responses['default'].schema.items.dump()
        ), [])

        # enum
        expect = {
            'enum':['available', 'pending', 'sold'],
            'type':'string'
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/findByStatus').get.parameters[0].items.dump()
        ), [])

        # type
        expect = {
            'type':'string'
        }
        self.assertEqual(_diff_(
            expect,
            self.app.resolve('#/definitions/pet:Pet').properties['photoUrls'].items.dump()
        ), [])

    def test_scope(self):
        """
        """
        # test scope in Swagger Object
        expect = {
            'write:pets':'Modify pets in your account',
            'read:pets':'Read your pets',
        }

        self.assertEqual(_diff_(
            expect,
            self.app.root.securityDefinitions['oauth2'].scopes
        ), [])

        # test scope in Operation Object
        expect = [dict(oauth2=['write:pets'])] 
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/store/order/{orderId}').delete.security
        ), [])

    def test_login_endpoint(self):
        """
        """
        expect = {
            'authorizationUrl':"http://petstore.swagger.wordnik.com/api/oauth/dialog",
        }

        self.assertEqual(_diff_(
            expect,
            self.app.root.securityDefinitions['oauth2'].dump(),
            include=['authorizationUrl']), [])

    def test_implicit(self):
        """ 
        """
        expect = {
            'type':'oauth2',
            'authorizationUrl':"http://petstore.swagger.wordnik.com/api/oauth/dialog",
            'flow':'implicit'
        }

        self.assertEqual(_diff_(
            expect,
            self.app.root.securityDefinitions['oauth2'].dump(),
            include=['type', 'authorizationUrl', 'flow']), [])

    def test_authorizations(self):
        """
        """
        expect = [dict(oauth2=['write:pets'])] 
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/store/order').post.security
        ), [])

    def test_authorization(self):
        """
        """
        expect={
            'authorizationUrl':'http://petstore.swagger.wordnik.com/api/oauth/dialog',
            'tokenUrl':'http://petstore.swagger.wordnik.com/api/oauth/token',
            'type':'oauth2',
            'flow':'implicit',
        }

        self.assertEqual(_diff_(
            expect,
            self.app.root.securityDefinitions['oauth2'].dump(),
            exclude=['scopes', ]
        ), [])

    def test_parameter(self):
        """
        """
        expect = {
            'name':'petId',
            'description':'ID of pet that needs to be fetched',
            'required':True,
            'type':'integer',
            'format':'int64',
            'minimum':1.0,
            'maximum':100000.0,
            'in':'path',
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/{petId}').get.parameters[0].dump()
        ), [])

        # allowMultiple, defaultValue, enum
        expect = {
            'collectionFormat':'csv',
            'default':['available'],
            'items':{
                'type':'string',
                'enum':['available', 'pending', 'sold']
            }
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/findByStatus').get.parameters[0].dump(),
            include=['collectionFormat', 'default', 'enum']
        ), [])

        # $ref, or Model as type
        expect = {
            'in':'body',
            'schema':{
                '$ref':'#/definitions/pet:Pet'
            }
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet').post.parameters[0].dump(),
            include=['schema', 'in']
        ), [])

    def test_operation(self):
        """
        """
        expect = {
            'operationId':'getPetById',
            'summary':'Find pet by ID',
            'description':'Returns a pet based on ID',
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/{petId}').get.dump(),
            include=['operationId', 'summary', 'description']
        ), [])

        # produces, consumes
        expect = {
            'produces':['application/json', 'application/xml'],
            'consumes':['application/json', 'application/xml']
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/{petId}').patch.dump(),
            include=['produces', 'consumes']
        ), [])

        # deprecated
        expect = dict(deprecated=True)
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/findByTags').get.dump(),
            include=['deprecated']
        ), [])

        # responses, in 1.2, the type of Operation is default response
        expect = {
            'schema':{
                'type':'array',
                'items': {
                    '$ref':'#/definitions/pet:Pet',
                }
            }
        }
        self.assertEqual(_diff_(
            expect,
            self.app.s('/api/pet/findByTags').get.responses['default'].dump()
        ), [])

    def test_property(self):
        """
        """
        expect = {
            "type":"integer",
            "format":"int32",
            "description":"User Status",
            "enum":[
                "1-registered",
                "2-active",
                "3-closed"
            ]
        }
        self.assertEqual(_diff_(
            expect,
            self.app.resolve('#/definitions/user:User').properties['userStatus'].dump()
        ), [])

    def test_model(self):
        """
        """
        expect = {
            "required":[
                "id",
                "name"
            ],
            "properties":{
                "id":{
                    "type":"integer",
                    "format":"int64",
                    "description":"unique identifier for the pet",
                    "minimum":0,
                    "maximum":100.0
                },
                "category":{
                    "$ref":"#/definitions/pet:Category"
                },
                "name":{
                    "type":"string"
                },
                "photoUrls":{
                    "type":"array",
                    "items":{
                        "type":"string"
                    }
                },
                "tags":{
                    "type":"array",
                    "items":{
                        "$ref":"#/definitions/pet:Tag"
                    }
                },
                "status":{
                    "type":"string",
                    "description":"pet status in the store",
                    "enum":[
                        "available",
                        "pending",
                        "sold"
                    ]
                }
            }
        }
        d = self.app.resolve('#/definitions/pet:Pet').dump()
        self.assertEqual(_diff_(
            expect,
            self.app.resolve('#/definitions/pet:Pet').dump()
        ), [])

    def test_info(self):
        """
        """
        expect = dict(
            version='1.0.0',
            title='Swagger Sample App',
            description='This is a sample server Petstore server.  You can find out more about Swagger \n    at <a href=\"http://swagger.wordnik.com\">http://swagger.wordnik.com</a> or on irc.freenode.net, #swagger.  For this sample,\n    you can use the api key \"special-key\" to test the authorization filters',
            termsOfService='http://helloreverb.com/terms/',
            contact=dict(
                email='apiteam@wordnik.com'
            ),
            license=dict(
                name='Apache 2.0',
                url='http://www.apache.org/licenses/LICENSE-2.0.html'
            )
        )
        self.assertEqual(_diff_(self.app.root.info.dump(), expect), [])

    def test_resource_list(self):
        """
        """
        expect = dict(
            swagger='2.0'
        )
        self.assertEqual(_diff_(
            expect,
            self.app.root.dump(),
            include=['swagger']
        ), [])


class Converter_v1_2_TestCase_Others(unittest.TestCase):
    """ for test cases needs special init
    """
    def test_token_endpoint(self):
        """
        """
        app = SwaggerApp.create(get_test_data_folder(
            version='1.2', which='simple_auth')
        )

        expect={
            'tokenUrl':'http://petstore.swagger.wordnik.com/api/oauth/token',
            'type':'oauth2',
            'flow':'access_code',
            'scopes': {
                'test:anything':'for testing purpose'        
            }
        }

        self.assertEqual(_diff_(
            expect,
            app.resolve('#/securityDefinitions/oauth2').dump()
        ), [])

    def test_authorization(self):
        """
        """
        app = SwaggerApp.create(get_test_data_folder(
            version='1.2', which='simple_auth')
        )
            
        expect = {
            'type':'apiKey',
            'in':'query',
            'name':'simpleQK'
        }
        self.assertEqual(_diff_(
            expect,
            app.resolve('#/securityDefinitions/simple_key').dump()
        ), [])

        expect = {
            'type':'apiKey',
            'in':'header',
            'name':'simpleHK'
        }
        self.assertEqual(_diff_(
            expect,
            app.resolve('#/securityDefinitions/simple_key2').dump()
        ), [])


        expect = {
            'type':'basic',
        }
        self.assertEqual(_diff_(
            expect,
            app.resolve('#/securityDefinitions/simple_basic').dump()
        ), [])

