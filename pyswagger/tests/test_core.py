from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.spec.base import BaseObj
import pyswagger
import unittest
import httpretty
import os


class SwaggerCoreTestCase(unittest.TestCase):
    """ test core part """

    def test_backward_compatible_v1_2(self):
        """ make sure alias works """
        self.assertEqual(pyswagger.SwaggerAuth, pyswagger.SwaggerSecurity)
        self.assertEqual(pyswagger.SwaggerApp._create_, pyswagger.SwaggerApp.create)

    @httpretty.activate
    def test_auto_schemes(self):
        """ make sure we scheme of url to access
        swagger.json as default scheme
        """
        # load swagger.json
        data = None
        with open(os.path.join(get_test_data_folder(
                version='2.0',
                which=os.path.join('schema', 'model')
                ), 'swagger.json')) as f:
            data = f.read()

        httpretty.register_uri(
            httpretty.GET,
            'http://test.com/api-doc/swagger.json',
            body=data
        )

        app = SwaggerApp._create_('http://test.com/api-doc/swagger.json')
        self.assertEqual(app.schemes, ['http'])

    @httpretty.activate
    def test_load_from_url_without_file(self):
        """ try to load from a url withou swagger.json """
        data = None
        with open(os.path.join(get_test_data_folder(
            version='2.0',
            which='wordnik'), 'swagger.json')) as f:
            data = f.read()

        httpretty.register_uri(
            httpretty.GET,
            'http://10.0.0.10:8080/swaggerapi/api/v1beta2',
            body=data
        )

        # no exception should be raised
        app = SwaggerApp.create('http://10.0.0.10:8080/swaggerapi/api/v1beta2')
        self.assertTrue(app.schemes, ['http'])
        self.assertTrue(isinstance(app.root, BaseObj))

