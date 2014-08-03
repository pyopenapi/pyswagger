from pyswagger import SwaggerApp
from .utils import get_test_data_folder
from pyswagger.obj import (
    Resource
)
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 


class SwaggerAppTestCase(unittest.TestCase):
    """ test SwaggerApp utility function """

    def test_field_name(self):
        """ field_name """
        self.assertEqual(sorted(app.schema._field_names_), sorted(['info', 'authorizations', 'apiVersion', 'swaggerVersion', 'apis']))

    def test_field_rename(self):
        """ renamed field name """
        op = app.schema.apis['pet'].apis['updatePet']
        self.assertEqual(sorted(op._field_names_), sorted([
            'authorizations',
            'consumes',
            'defaultValue',
            'deprecated',
            'enum',
            'format',
            'items',
            'maximum',
            'method',
            'minimum',
            'nickname',
            'parameters',
            'path',
            'produces',
            'ref',
            'responseMessages',
            'type',
            'uniqueItems'
        ]))

    def test_children(self):
        """ children """
        chd = app.schema._children_
        self.assertEqual(len(chd), 5)
        self.assertEqual(set(['user', 'pet', 'store']), set([c[0] for c in chd if isinstance(c[1], Resource)]))

