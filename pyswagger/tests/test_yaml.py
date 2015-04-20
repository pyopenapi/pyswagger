from pyswagger import SwaggerApp
from pyswagger.consts import FILE_TYPE_YAML
from .utils import get_test_data_folder
import unittest


class YAMLTestCase(unittest.TestCase):
    """ test yaml loader support """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which='yaml',
            ),
            type_hint=FILE_TYPE_YAML
        )

    def test_schema(self):
        """ make sure schema is loaded """
        op = self.app.s('/pet').post
        self.assertEqual(op.tags, ['pet'])
        self.assertEqual(op.operationId, 'addPet')
