from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.obj import (
    Parameter,
    Items)
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))


class DataTypeTestCase(unittest.TestCase):
    """ make sure data type ready """

    def test_operation(self):
        """ operation """ 
        op = app._schema_.apis['pet'].apis['findPetsByStatus']
        self.assertEqual(op.type, 'array')
        self.assertEqual(op.items.ref, 'Pet')

    def test_parameter(self):
        """ parameter """ 
        p = app._schema_.apis['pet'].apis['findPetsByStatus'].parameters[0]
        self.assertTrue(isinstance(p, Parameter))
        self.assertEqual(p.required, True)
        self.assertEqual(p.defaultValue, 'available')
        self.assertEqual(p.type, 'string')
        self.assertTrue(isinstance(p.enum, list))
        self.assertEqual(sorted(p.enum), sorted(['available', 'pending', 'sold']))

    def test_property(self):
        """ property """ 
        p = app._schema_.apis['pet'].models['Pet'].properties
        # id
        self.assertEqual(p['id'].type, 'integer')
        self.assertEqual(p['id'].format, 'int64')
        self.assertEqual(p['id'].minimum, 0.0)
        self.assertEqual(p['id'].maximum, 100.0)
        # category
        self.assertEqual(p['category'].ref, 'Category')
        # name
        self.assertEqual(p['name'].type, 'string')
        # photoUrls
        self.assertEqual(p['photoUrls'].type, 'array')
        self.assertTrue(isinstance(p['photoUrls'].items, Items))
        self.assertEqual(p['photoUrls'].items.type, 'string')
        # tag
        self.assertEqual(p['tags'].type, 'array')
        self.assertTrue(isinstance(p['tags'].items, Items))
        self.assertEqual(p['tags'].items.ref, 'Tag')
        # status
        self.assertEqual(p['status'].type, 'string')
        self.assertEqual(sorted(p['status'].enum), sorted(['available', 'pending', 'sold']))

