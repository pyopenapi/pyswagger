from pyswagger import SwaggerApp, SwaggerAuth
from .utils import get_test_data_folder
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='simple_auth')) 


class BasicAuthAndApiKeyTestCase(unittest.TestCase):
    """ test cases for authorzation related """

    def setUp(self):
        self.auth = SwaggerAuth(app)
        self.auth.update_with('simple_key', '123456')
        self.auth.update_with('simple_basic', ('mission', '123123'))
        self.auth.update_with('simple_basic2', ('qoo', '456456'))
        self.auth.update_with('simple_key2', '789789')

    def test_deleteUser(self):
        """ basic auth """
        req, _ = app.op['deleteUser'](username='mission')
        self.auth(req).prepare()

        self.assertTrue('Authorization' in req.header)
        self.assertEqual(req.header['Authorization'], 'Basic bWlzc2lvbjoxMjMxMjM=')

    def test_getUserByName(self):
        """ api key, passed by query """
        req, _ = app.op['getUserByName'](username='mission')
        self.auth(req).prepare()

        self.assertTrue('simpleQK' in req.query)
        self.assertEqual(req.query['simpleQK'], '123456')

    def test_createUser(self):
        """ api key, passed by header """
        req, _ = app.op['createUser'](body=dict(id=0, username='mission', firstName='liao', lastName='mission'))
        self.auth(req).prepare()

        self.assertTrue('simpleHK' in req.header)
        self.assertEqual(req.header['simpleHK'], '789789')

    def test_getAllUsers(self):
        """ test global auth """
        req, _ = app.op['getAllUsers']()
        self.auth(req).prepare()

        self.assertTrue('Authorization' in req.header)
        self.assertEqual(req.header['Authorization'], 'Basic cW9vOjQ1NjQ1Ng==')


class NoAuthProvidedTestCase(unittest.TestCase):
    """ nothing is altered when nothing is provided """

    def setUp(self):
        self.auth = SwaggerAuth(app)
 
    def test_deleteUser(self):
        """ basic auth """
        req, _ = app.op['deleteUser'](username='mission')
        self.auth(req).prepare()

        self.assertFalse('Authorization' in req.header)

    def test_getUserByName(self):
        """ api key, passed by query """
        req, _ = app.op['getUserByName'](username='mission')
        self.auth(req).prepare()

        self.assertFalse('simpleQK' in req.query)

    def test_createUser(self):
        """ api key, passed by header """
        req, _ = app.op['createUser'](body=dict(id=0, username='mission', firstName='liao', lastName='mission'))
        self.auth(req).prepare()

        self.assertFalse('simpleHK' in req.header)

    def test_getAllUsers(self):
        """ test global auth """
        req, _ = app.op['getAllUsers']()
        self.auth(req).prepare()

        self.assertFalse('Authorization' in req.header)

