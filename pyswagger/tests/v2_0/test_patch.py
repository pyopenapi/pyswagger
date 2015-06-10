from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest


_json = 'application/json'
_xml = 'application/xml'


class PatchObjTestCase(unittest.TestCase):
    """ test patch_obj.py """
    
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(
            version='2.0',
            which='patch'
        ))

    def test_operation_produces_consumes(self):
        """ test patch Operation with produces and
        consumes
        """
        p = self.app.s('/pc')

        self.assertEqual(p.get.produces, [_json])
        self.assertEqual(p.get.consumes, [_json])
        self.assertEqual(p.post.produces, [_xml])
        self.assertEqual(p.post.consumes, [_json])
        self.assertEqual(p.put.produces, [_json])
        self.assertEqual(p.put.consumes, [_xml])
        self.assertEqual(p.delete.produces, [_xml])
        self.assertEqual(p.delete.consumes, [_xml])

    def test_operation_parameters(self):
        """ test patch Operation with parameters """
        p = self.app.s('/param')

        pp = p.get.parameters
        self.assertEqual(len(pp), 2)

        self.assertEqual(pp[0].name, 'p1')
        self.assertEqual(getattr(pp[0], 'in'), 'query')
        self.assertEqual(getattr(pp[0], 'type'), 'string')
        self.assertEqual(pp[1].name, 'p2')
        self.assertEqual(getattr(pp[1], 'in'), 'query')
        self.assertEqual(getattr(pp[1], 'type'), 'string')

        pp = p.post.parameters
        self.assertEqual(len(pp), 2)

        self.assertEqual(pp[0].name, 'p1')
        self.assertEqual(getattr(pp[0], 'in'), 'path')
        self.assertEqual(getattr(pp[0], 'type'), 'string')
        self.assertEqual(pp[1].name, 'p2')
        self.assertEqual(getattr(pp[1], 'in'), 'query')
        self.assertEqual(getattr(pp[1], 'type'), 'string')

    def test_operation_scheme(self):
        """ test patch Operation with scheme """
        p = self.app.s('/s')

        self.assertEqual(p.get.cached_schemes, self.app.root.schemes)
        self.assertEqual(p.get.cached_schemes, ['http', 'https'])

    def test_path_item(self):
        """ test patch PathItem """
        p = self.app.s('/pc')

        self.assertEqual(p.get.method, 'get')
        self.assertEqual(p.get.url, 'test.com/v1/pc')
        self.assertEqual(p.get.path, '/pc')
        self.assertEqual(p.get.base_path, '/v1')

    def test_schema(self):
        """ test patch Schema """
        s = self.app.resolve('#/definitions/schema1')

        self.assertEqual(s.name, 'schema1')
