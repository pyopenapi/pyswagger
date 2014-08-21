from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger import prim
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 


class SwaggerRequest_Pet_TestCase(unittest.TestCase):
    """ test SwaggerRequest from Operation's __call__ """

    def test_updatePet(self):
        """ Pet.updatePet """
        req, _ = app.op['updatePet'](body=dict(id=1, name='Mary', category=dict(id=1, name='dog')))
        self.assertEqual(req.verb, 'PUT')
        self.assertEqual(req.header, {'Accept': 'application/json'})

        m = req.data['body']
        self.assertTrue(isinstance(m, prim.Model))
        self.assertEqual(m.id, 1)
        self.assertEqual(m.name, 'Mary')
        self.assertTrue(isinstance(m.category, prim.Model))
        self.assertEqual(m.category.id, 1)
        self.assertEqual(m.category.name, 'dog')

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet')
        self.assertEqual(req.query, {})

    def test_findPetsByStatus(self):
        """ Pet.findPetsByStatus """
        req, _ = app.op['findPetsByStatus'](status='available')
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/findByStatus')
        self.assertEqual(req.verb, 'GET')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, {})
        self.assertEqual(req.query, {'status': 'available'})

    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        req, _ = app.op['findPetsByTags'](tags=['small', 'cute', 'north'])
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/findByTags')
        self.assertEqual(req.verb, 'GET')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, {})
        self.assertEqual(req.query, {'tags': ['small', 'cute', 'north']})

    def test_partialUpdate(self):
        """ Pet.partialUpdate """
        req, _ = app.op['partialUpdate'](petId=0, body=dict(id=2, name='Tom', category=dict(id=2, name='cat'), tags=[dict(id=0, name='cute'), dict(id=1, name='small')]))
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/0')
        self.assertEqual(req.verb, 'PATCH')
        self.assertEqual(req.header, {'Accept': 'application/json'})

        m = req.data['body']
        self.assertTrue(isinstance(m, prim.Model))
        self.assertEqual(m.id, 2)
        self.assertEqual(m.name, 'Tom')
        self.assertEqual(m.photoUrls, None)
        self.assertEqual(m.status, None)

        self.assertTrue(isinstance(m.category, prim.Model))
        mm = m.category
        self.assertEqual(mm.id, 2)
        self.assertEqual(mm.name, 'cat')

        self.assertTrue(isinstance(m.tags, prim.Array))
        self.assertEqual(len(m.tags), 2)
        self.assertTrue(isinstance(m.tags[0], prim.Model))
        self.assertEqual(m.tags[0].id, 0)
        self.assertEqual(m.tags[0].name, 'cute')
        self.assertTrue(isinstance(m.tags[1], prim.Model))
        self.assertEqual(m.tags[1].id, 1)
        self.assertEqual(m.tags[1].name, 'small')

        self.assertEqual(req.query, {})

    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm """
        req, _ = app.op['updatePetWithForm'](petId=23, name='Gary', status='pending')
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/23')
        self.assertEqual(req.verb, 'POST')
        self.assertEqual(req.header,{
            'Content-Type': u'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        })
        self.assertEqual(req.data, {u'status': 'pending', u'name': 'Gary'})
        self.assertEqual(req.query, {})

    def test_addPet(self):
        """ Pet.addPet """
        req, _ = app.op['addPet'](body=dict(id=34, name='Qoo', category=dict(id=2, name='cat'), status='available'))
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet')
        self.assertEqual(req.verb, 'POST')
        self.assertEqual(req.header, {'Accept': 'application/json'})

        m = req.data['body']
        self.assertTrue(isinstance(m, prim.Model))
        self.assertEqual(m.id, 34)
        self.assertEqual(m.name, 'Qoo')
        self.assertEqual(m.status, 'available')

        mm = m.category
        self.assertTrue(isinstance(mm, prim.Model))
        self.assertEqual(mm.id, 2)
        self.assertEqual(mm.name, 'cat')

        self.assertEqual(req.query, {})

    def test_deletePet(self):
        """ Pet.deletePet """
        req, _ = app.op['deletePet'](petId=22)
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/22')
        self.assertEqual(req.verb, 'DELETE')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, {})
        self.assertEqual(req.query, {})

    def test_getPetById(self):
        """ Pet.getPetById """
        req, _ = app.op['getPetById'](petId=100)
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/100')
        self.assertEqual(req.verb, 'GET')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, {})
        self.assertEqual(req.query, {})

    def test_uploadFile(self):
        """ Pet.uploadFile """
        # TODO: implement File upload


class SwaggerResponse_TestCase(unittest.TestCase):
    """ test SwaggerResponse from Pet's Operation's __call__ """

    def test_updatePet(self):
        """ Pet.updatePet """
        _, resp = app.op['updatePet'](body=dict(id=1, name='Mary'))

        # update raw before status should raise exception
        self.assertRaises(Exception, resp.apply_with, raw={})

        resp.apply_with(status=400)
        self.assertEqual(resp.message, 'Invalid ID supplied')
        resp.apply_with(status=404)
        self.assertEqual(resp.message, 'Pet not found')
        resp.apply_with(status=405)
        self.assertEqual(resp.message, 'Validation exception')

    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        _, resp = app.op['findPetsByTags'](tags=[])

        resp.apply_with(status=200, raw=[
            dict(id=1, name='Tom', category=dict(id=1, name='dog'), tags=[dict(id=1, name='small')]),
            dict(id=2, name='QQ', tags=[dict(id=1, name='small')])
        ])
        self.assertEqual(resp.message, '')

        d = resp.data
        self.assertTrue(isinstance(d, prim.Array))
        d1 = d[0]
        self.assertTrue(isinstance(d1, prim.Model))
        self.assertEqual(d1.id, 1)
        self.assertEqual(d1.name, 'Tom')
        self.assertEqual(d1.tags, [dict(id=1, name='small')])
        self.assertEqual(d1.tags[0].name, 'small')

    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm, test void """
        _, resp = app.op['updatePetWithForm'](petId=23)

        resp.apply_with(status=200, raw={})
        self.assertEqual(resp.data, None)
        self.assertTrue(isinstance(resp.data, prim.Void))

