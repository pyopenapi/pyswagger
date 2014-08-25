from __future__ import absolute_import
from pyswagger import SwaggerApp, prim
from pyswagger.contrib.client.requests import SwaggerClient
from ...utils import get_test_data_folder
import unittest
import httpretty
import json


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 
client = SwaggerClient(app)


pet_Tom = dict(id=1, name='Tom', tags=[dict(id=0, name='available'), dict(id=1, name='sold')])
pet_Qoo = dict(id=2, name='Qoo', tags=[dict(id=0, name='available')])
pet_Sue = dict(id=3, name='Sue', tags=[dict(id=0, name='available')])
pet_Kay = dict(id=4, name='Kay', category=dict(id=2, name='cat'), status='available')


class RequestsClient_Pet_TestCase(unittest.TestCase):
    """ test SwaggerClient implemented by requests """

    @httpretty.activate
    def test_updatePet(self):
        """ Pet.updatePet """
        httpretty.register_uri(
            httpretty.PUT,
            'http://petstore.swagger.wordnik.com/api/pet',
            status=200
        )

        resp = client.request(app.op['updatePet'](body=dict(id=1, name='Mary', category=dict(id=1, name='dog'))))

        self.assertEqual(httpretty.last_request().method, 'PUT')
        self.assertEqual(httpretty.last_request().headers['content-type'], 'application/json')
        self.assertEqual(httpretty.last_request().body, '{"body": {"category": {"id": 1, "name": "dog"}, "status": null, "name": "Mary", "tags": null, "photoUrls": null, "id": 1}}')

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.header['content-type'], 'text/plain; charset=utf-8')

    @httpretty.activate
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
        self.assertTrue(isinstance(resp.data, prim.Array))
        self.assertTrue(len(resp.data), 2)
        self.assertTrue(isinstance(resp.data[0], prim.Model))
        self.assertEqual(resp.data[0].id, 1)
        self.assertEqual(resp.data[0].name, 'Tom')
        self.assertTrue(isinstance(resp.data[0].tags, prim.Array))

    @httpretty.activate
    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/findByTags',
            status=200,
            body=json.dumps([pet_Tom, pet_Qoo])
        )

        resp = client.request(app.op['findPetsByTags'](tags=['small', 'cute', 'north']))

        self.assertEqual(httpretty.last_request().querystring, dict(tags=['small,cute,north']))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, prim.Array))
        self.assertTrue(len(resp.data), 2)
        self.assertTrue(isinstance(resp.data[0], prim.Model))
        self.assertEqual(resp.data[1].id, 2)
        self.assertEqual(resp.data[1].name, 'Qoo')
        self.assertTrue(isinstance(resp.data[1].tags, prim.Array))

    @httpretty.activate
    def test_partialUpdate(self):
        """ Pet.partialUpdate """
        httpretty.register_uri(httpretty.PATCH, 'http://petstore.swagger.wordnik.com/api/pet/0',
            status=200,
            body=json.dumps([pet_Tom, pet_Sue])
        )
        resp = client.request(app.op['partialUpdate'](
            petId=0,
            body=pet_Tom
        ))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, prim.Array))
        self.assertEqual(resp.data[1].id, 3)
        self.assertEqual(resp.data[1].name, 'Sue')
        self.assertTrue(isinstance(resp.data[1].tags, prim.Array))

    @httpretty.activate
    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm """
        httpretty.register_uri(httpretty.POST, 'http://petstore.swagger.wordnik.com/api/pet/0',
            status=200)

        resp = client.request(app.op['updatePetWithForm'](petId=0, name='Gary', status='pending'))

        self.assertEqual(httpretty.last_request().parsed_body, {u'status': [u'pending'], u'name': [u'Gary']})

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)

    @httpretty.activate
    def test_addPet(self):
        """ Pet.addPet """
        httpretty.register_uri(httpretty.POST, 'http://petstore.swagger.wordnik.com/api/pet',
            status=200)

        resp = client.request(app.op['addPet'](body=pet_Kay))

        self.assertEqual(httpretty.last_request().parsed_body, {u'body': {u'category': {u'id': 2, u'name': u'cat'}, u'status': u'available', u'name': u'Kay', u'tags': None, u'photoUrls': None, u'id': 4}})

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)

    @httpretty.activate
    def test_deletePet(self):
        """ Pet.deletePet """
        httpretty.register_uri(httpretty.DELETE, 'http://petstore.swagger.wordnik.com/api/pet/22',
            status=200)
 
        resp = client.request(app.op['deletePet'](petId=22))

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, None)
        self.assertTrue(isinstance(resp.data, prim.Void))

    @httpretty.activate
    def test_getPetById(self):
        """ Pet.getPetById """
        httpretty.register_uri(httpretty.GET, 'http://petstore.swagger.wordnik.com/api/pet/1',
            status=200,
            body=json.dumps(pet_Tom)
        )

        resp = client.request(app.op['getPetById'](petId=1))

        self.assertEqual(resp.status, 200)
        self.assertTrue(isinstance(resp.data, prim.Model))
        self.assertEqual(resp.data, {u'category': None, u'status': None, u'name': 'Tom', u'tags': [{u'id': 0, u'name': 'available'}, {u'id': 1, u'name': 'sold'}], u'photoUrls': None, u'id': 1})

    @httpretty.activate
    def test_uploadFile(self):
        """ Pet.uploadFile """
        # TODO: implement File upload
