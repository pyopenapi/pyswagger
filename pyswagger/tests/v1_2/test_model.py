from pyswagger import SwaggerApp
from pyswagger.contrib.client.requests import Client
from pyswagger.primitives import Model
from ..utils import get_test_data_folder
import unittest
import httpretty
import json
import pytest
import sys


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='model_subtypes')) 
client = Client()

u_mission = dict(id=1, username='mission', password='123123')
uwi_mary = dict(id=2, username='mary', password='456456', email='m@a.ry', phone='123')
uwi_kevin = dict(id=3, username='kevin')


@pytest.mark.skipif(sys.version_info[:2] >= (3, 3), reason='httpretty corrupt in python3')
class ModelInteritanceTestCase(unittest.TestCase):
    """ test cases for model inheritance """

    @httpretty.activate
    def test_inheritantce_full(self):
        """ init a Model with every property along
        the inheritance path.
        """
        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/user/mary',
            status=200,
            body=json.dumps(uwi_mary)
            )

        resp = client.request(app.op['getUserByName'](username='mary'))

        self.assertTrue(isinstance(resp.data, Model))
        m = resp.data
        self.assertEqual(m.id, 2)
        self.assertEqual(m.username, 'mary')
        self.assertEqual(m.email, 'm@a.ry')
        self.assertEqual(m.phone, '123')
        self.assertEqual(m.sub_type, 'UserWithInfo')

    @httpretty.activate
    def test_inheritance_partial(self):
        """ init a Model with only partial property
        set, expect failed.
        """
        httpretty.register_uri(
            httpretty.GET, 'http://petstore.swagger.wordnik.com/api/user/kevin',
            status=200,
            body=json.dumps(uwi_kevin)
            )

        resp = client.request(app.op['getUserByName'](username='kevin'))

        self.assertTrue(isinstance(resp.data, Model))
        m = resp.data
        self.assertEqual(m.id, 3)
        self.assertEqual(m.username, 'kevin')
        self.assertTrue('email' not in m)
        self.assertTrue('phone' not in m)
        self.assertEqual(m.sub_type, 'UserWithInfo')

    def test_inheritance_root(self):
        """ make sure we could init a root Model """
        req, _ = app.op['createUser'](body=u_mission)
        req.prepare()

        self.assertTrue(isinstance(req._p['body']['body'], Model))
        m = req._p['body']['body']
        self.assertEqual(m.id, 1)
        self.assertEqual(m.username, 'mission')
        self.assertEqual(m.sub_type, 'User')
        self.assertRaises(KeyError, getattr, m, 'email')
        self.assertRaises(KeyError, getattr, m, 'email')

