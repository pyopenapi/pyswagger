from __future__ import absolute_import
from pyswagger import SwaggerApp
from pyswagger.contrib.client.requests import Client
from ...utils import get_test_data_folder
from ....primitives import Model, Array
import unittest
import httpretty
import json
import six


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 
client = Client()


pet_Tom = dict(id=1, name='Tom', tags=[dict(id=0, name='available'), dict(id=1, name='sold')])
pet_Qoo = dict(id=2, name='Qoo', tags=[dict(id=0, name='available')])
pet_Sue = dict(id=3, name='Sue', tags=[dict(id=0, name='available')])
pet_Kay = dict(id=4, name='Kay', category=dict(id=2, name='cat'), status='available', photoUrls=None, tags=None)
pet_QQQ = dict(id=1, name='QQQ', category=dict(id=1, name='dog'), tags=None, status=None)


@httpretty.activate
class RequestsClient_Pet_TestCase(unittest.TestCase):
    """ test SwaggerClient implemented by requests """

    def test_updatePet(self):
        """ Pet.updatePet """
        httpretty.register_uri(
            httpretty.PUT,
            'http://petstore.swagger.wordnik.com/api/pet',
            status=200
        )

        resp = client.request(app.op['updatePet'](body=pet_QQQ))

        self.assertEqual(httpretty.last_request().method, 'PUT')
        self.assertEqual(httpretty.last_request().headers['content-type'], 'application/json')
        self.assertTrue(json.loads(httpretty.last_request().body.decode('utf-8')), pet_QQQ)

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.header['content-type'][0], 'text/plain; charset=utf-8')

    def test_findPetsByStatus(self):
        """ Pet.findPetsByStatus """
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/findByStatus',
            status=200,
            content_type='application/json',
            body=json.dumps([pet_Tom])
        )

        resp = client.request(app.op['findPetsByStatus'](status=['available', 'sold']))

        self.assertEqual(httpretty.last_request().querystring, dict(status=['available,sold']))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, Array))
        self.assertTrue(len(resp.data), 2)
        self.assertTrue(isinstance(resp.data[0], Model))
        self.assertEqual(resp.data[0].id, 1)
        self.assertEqual(resp.data[0].name, 'Tom')
        self.assertTrue(isinstance(resp.data[0].tags, Array))

    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/findByTags',
            status=200,
            content_type='application/json',
            body=json.dumps([pet_Tom, pet_Qoo])
        )

        resp = client.request(app.op['findPetsByTags'](tags=['small', 'cute', 'north']))

        self.assertEqual(httpretty.last_request().querystring, dict(tags=['small,cute,north']))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, Array))
        self.assertTrue(len(resp.data), 2)
        self.assertTrue(isinstance(resp.data[0], Model))
        self.assertEqual(resp.data[1].id, 2)
        self.assertEqual(resp.data[1].name, 'Qoo')
        self.assertTrue(isinstance(resp.data[1].tags, Array))

    def test_partialUpdate(self):
        """ Pet.partialUpdate """
        httpretty.register_uri(httpretty.PATCH, 'http://petstore.swagger.wordnik.com/api/pet/0',
            status=200,
            content_type='application/json',
            body=json.dumps([pet_Tom, pet_Sue])
        )
        resp = client.request(app.op['partialUpdate'](
            petId=0,
            body=pet_Tom
        ))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, Array))
        self.assertEqual(resp.data[1].id, 3)
        self.assertEqual(resp.data[1].name, 'Sue')
        self.assertTrue(isinstance(resp.data[1].tags, Array))

    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm """
        httpretty.register_uri(httpretty.POST, 'http://petstore.swagger.wordnik.com/api/pet/0',
            status=200)

        resp = client.request(app.op['updatePetWithForm'](petId=0, name='Gary', status='pending'))

        self.assertEqual(httpretty.last_request().parsed_body, {u'status': [u'pending'], u'name': [u'Gary']})

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)

    def test_addPet(self):
        """ Pet.addPet """
        httpretty.register_uri(httpretty.POST, 'http://petstore.swagger.wordnik.com/api/pet',
            status=200)

        resp = client.request(app.op['addPet'](body=pet_Kay))

        self.assertEqual(httpretty.last_request().parsed_body, pet_Kay)

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)

    def test_deletePet(self):
        """ Pet.deletePet """
        httpretty.register_uri(httpretty.DELETE, 'http://petstore.swagger.wordnik.com/api/pet/22',
            status=200)
 
        resp = client.request(app.op['deletePet'](petId=22))

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)

    def test_getPetById(self):
        """ Pet.getPetById """
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/1',
            status=200,
            content_type='application/json',
            body=json.dumps(pet_Tom)
        )

        resp = client.request(app.op['getPetById'](petId=1))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, Model))
        self.assertEqual(resp.data,
            {u'name': 'Tom', u'tags': [{u'id': 0, u'name': 'available'}, {u'id': 1, u'name': 'sold'}], u'id': 1}
            )

    def test_uploadFile(self):
        """ Pet.uploadFile """
        httpretty.register_uri(httpretty.POST, 'http://petstore.swagger.wordnik.com/api/pet/uploadImage',
            status=200)

        resp = client.request(app.op['uploadFile'](
            additionalMetadata='a test image', file=dict(data=six.StringIO('a test Content'), filename='test.txt')))

        self.assertEqual(resp.status, 200)

        body = httpretty.last_request().body.decode()
        self.assertTrue(body.find('additionalMetadata') != -1)
        self.assertTrue(body.find('a test image') != -1)
        self.assertTrue(body.find('file') != -1)
        self.assertTrue(body.find('a test Content') != -1)
        self.assertTrue(body.find('filename="test.txt"') != -1)

@httpretty.activate
class RequestsOptTestCase(unittest.TestCase):
    """ make sure that passing options to requests won't fail """

    def test_verify(self):
        """ option for send: verify """
        client = Client(send_opt=dict(verify=False))

        # testing this client with getPetById
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/1',
            status=200,
            content_type='application/json',
            body=json.dumps(pet_Tom)
        )

        resp = client.request(app.op['getPetById'](petId=1))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, Model))
        self.assertEqual(resp.data,
            {u'name': 'Tom', u'tags': [{u'id': 0, u'name': 'available'}, {u'id': 1, u'name': 'sold'}], u'id': 1}
            )
