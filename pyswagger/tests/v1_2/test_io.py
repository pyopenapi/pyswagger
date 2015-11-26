from pyswagger import SwaggerApp, errs
from ..utils import get_test_data_folder
from pyswagger.primitives import Model, Array
from pyswagger.io import SwaggerRequest
import unittest
import json


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 


class SwaggerRequest_Pet_TestCase(unittest.TestCase):
    """ test SwaggerRequest from Operation's __call__ """

    def test_updatePet(self):
        """ Pet.updatePet """
        req, _ = app.op['updatePet'](body=dict(id=1, name='Mary', category=dict(id=1, name='dog')))
        req.prepare()

        self.assertEqual(req.method, 'put')
        self.assertEqual(req.header, {'Content-Type': 'application/json', 'Accept': 'application/json'})
        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet')
        self.assertEqual(req.path, '/api/pet')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.query, [])

        m = req._p['body']['body']
        self.assertTrue(isinstance(m, Model))
        self.assertEqual(m.id, 1)
        self.assertEqual(m.name, 'Mary')
        self.assertTrue(isinstance(m.category, Model))
        self.assertEqual(m.category.id, 1)
        self.assertEqual(m.category.name, 'dog')

    def test_findPetsByStatus(self):
        """ Pet.findPetsByStatus """
        req, _ = app.op['findPetsByStatus'](status=['available', 'sold'])
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/findByStatus')
        self.assertEqual(req.path, '/api/pet/findByStatus')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.method, 'get')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, None)
        self.assertEqual(req.query, [('status', 'available,sold')])

    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        req, _ = app.op['findPetsByTags'](tags=['small', 'cute', 'north'])
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/findByTags')
        self.assertEqual(req.path, '/api/pet/findByTags')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.method, 'get')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, None)
        self.assertEqual(req.query, [('tags', 'small,cute,north')])

    def test_partialUpdate(self):
        """ Pet.partialUpdate """
        req, _ = app.op['partialUpdate'](petId=0, body=dict(id=2, name='Tom', category=dict(id=2, name='cat'), tags=[dict(id=0, name='cute'), dict(id=1, name='small')]))
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/0')
        self.assertEqual(req.path, '/api/pet/0')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.method, 'patch')
        self.assertEqual(req.header, {'Content-Type': 'application/json', 'Accept': 'application/json'})

        m = req._p['body']['body']
        self.assertTrue(isinstance(m, Model))
        self.assertEqual(m.id, 2)
        self.assertEqual(m.name, 'Tom')
        self.assertTrue('photoUrls' not in m)
        self.assertTrue('status' not in m)

        self.assertTrue(isinstance(m.category, Model))
        mm = m.category
        self.assertEqual(mm.id, 2)
        self.assertEqual(mm.name, 'cat')

        self.assertTrue(isinstance(m.tags, Array))
        self.assertEqual(len(m.tags), 2)
        self.assertTrue(isinstance(m.tags[0], Model))
        self.assertEqual(m.tags[0].id, 0)
        self.assertEqual(m.tags[0].name, 'cute')
        self.assertTrue(isinstance(m.tags[1], Model))
        self.assertEqual(m.tags[1].id, 1)
        self.assertEqual(m.tags[1].name, 'small')

        self.assertEqual(req.query, [])

    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm """
        req, _ = app.op['updatePetWithForm'](petId=23, name='Gary', status='pending')
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/23')
        self.assertEqual(req.path, '/api/pet/23')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.method, 'post')
        self.assertEqual(req.header,{
            'Content-Type': u'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        })
        self.assertTrue(req.data.find('status=pending') != -1)
        self.assertTrue(req.data.find('name=Gary') != -1)
        self.assertEqual(req.query, [])

    def test_addPet(self):
        """ Pet.addPet """
        req, _ = app.op['addPet'](body=dict(id=34, name='Qoo', category=dict(id=2, name='cat'), status='available'))
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet')
        self.assertEqual(req.path, '/api/pet')
        self.assertEqual(req.base_path, '')
        self.assertEqual(req.method, 'post')
        self.assertEqual(req.header, {'Content-Type': 'application/json', 'Accept': 'application/json'})

        m = req._p['body']['body']
        self.assertTrue(isinstance(m, Model))
        self.assertEqual(m.id, 34)
        self.assertEqual(m.name, 'Qoo')
        self.assertEqual(m.status, 'available')

        mm = m.category
        self.assertTrue(isinstance(mm, Model))
        self.assertEqual(mm.id, 2)
        self.assertEqual(mm.name, 'cat')

        self.assertEqual(req.query, [])

    def test_deletePet(self):
        """ Pet.deletePet """
        req, _ = app.op['deletePet'](petId=22)
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/22')
        self.assertEqual(req.path, '/api/pet/22')
        self.assertEqual(req.method, 'delete')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, None)
        self.assertEqual(req.query, [])

    def test_getPetById(self):
        """ Pet.getPetById """
        req, _ = app.op['getPetById'](petId=100)
        req.prepare()

        self.assertEqual(req.url, 'http://petstore.swagger.wordnik.com/api/pet/100')
        self.assertEqual(req.path, '/api/pet/100')
        self.assertEqual(req.method, 'get')
        self.assertEqual(req.header, {'Accept': 'application/json'})
        self.assertEqual(req.data, None)
        self.assertEqual(req.query, [])

    def test_opt_url_netloc(self):
        """ test the replace of net loc """
        req, _ = app.op['getPetById'](petId=100)
        req.prepare()

        req._patch({SwaggerRequest.opt_url_netloc: 'localhost:9001'})
        self.assertEqual(req.url, 'http://localhost:9001/api/pet/100')
        self.assertEqual(req.path, '/api/pet/100')

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
        self.assertEqual(resp.status, 400)

    def test_findPetsByTags(self):
        """ Pet.findPetsByTags """
        _, resp = app.op['findPetsByTags'](tags=[])

        raw = json.dumps([
            dict(id=1, name='Tom', category=dict(id=1, name='dog'), tags=[dict(id=1, name='small')]),
            dict(id=2, name='QQ', tags=[dict(id=1, name='small')])
        ])

        resp.apply_with(status=200, raw=raw)

        d = resp.data
        self.assertTrue(isinstance(d, Array))
        d1 = d[0]
        self.assertTrue(isinstance(d1, Model))
        self.assertEqual(d1.id, 1)
        self.assertEqual(d1.name, 'Tom')
        self.assertEqual(d1.tags, [dict(id=1, name='small')])
        self.assertEqual(d1.tags[0].name, 'small')

    def test_updatePetWithForm(self):
        """ Pet.updatePetWithForm, test void """
        _, resp = app.op['updatePetWithForm'](petId=23)

        resp.apply_with(status=200, raw={})
        self.assertEqual(resp.data, None)

    def test_invalid_enum(self):
        """ invalid enum value """
        self.assertRaises(errs.ValidationError, app.op['findPetsByStatus'], status=['wrong_enum'])

    def test_default_value(self):
        """ make sure defaultValue works """
        req, _ = app.op['findPetsByStatus']()
        self.assertEqual(req._p['query'], [(u'status', 'available')])

        # when there is no defaultValue, we should not provide a 'None'
        req, _ = app.op['updatePetWithForm'](petId=1, name='Tom')
        self.assertEqual(req._p['formData'], [('name', 'Tom')])

        req, _ = app.op['updatePetWithForm'](petId=1)
        self.assertEqual(req._p['formData'], [])

    def test_min_max(self):
        """ make sure minimum/maximum works """
        self.assertRaises(errs.ValidationError, app.op['getPetById'], petId=-100)
        self.assertRaises(errs.ValidationError, app.op['getPetById'], petId=1000000)

