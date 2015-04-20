from pyswagger import SwaggerApp, io, primitives
from ..utils import get_test_data_folder
import unittest
import os


class SwaggerResponseTestCase(unittest.TestCase):
    """ test SwaggerResponse """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('io', 'response')
        ))

    def test_response_schema_with_status(self):
        """ make sure schema works as expected """
        resp = io.SwaggerResponse(self.app.s('/resp').get)

        # make sure exception raised
        self.assertRaises(Exception, resp.apply_with, None, 'some string')

        # test for 'default'
        resp.apply_with(0, 'test string')
        self.assertEqual(resp.status, 0)
        self.assertEqual(resp.raw, 'test string')
        self.assertEqual(resp.data, 'test string')

        # test for specific status code
        r = '{"id": 0, "message": "test string 2"}'
        resp.apply_with(404, r)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.raw, r)
        self.assertTrue(isinstance(resp.data, primitives.Model))

    def test_error_only_status(self):
        """ it's legal for a Swagger without any successful status Response object.
        in this case, users need to access response via SwaggerResponse.raw
        """
        resp = io.SwaggerResponse(self.app.s('/resp').post)

        # make sure we are ok when no matching status and without a 'default'
        resp.apply_with(200, 'some data')
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.raw, 'some data')
        self.assertEqual(resp.data, None)

        # make sure header also works fine
        header = {
            'A': 1,
            'B': '222'
        }
        resp.apply_with(200, None, header)
        self.assertEqual(resp.header, {
            'A': [1],
            'B': ['222']
        })
