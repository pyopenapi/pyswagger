from pyswagger import SwaggerApp, utils
from ..utils import get_test_data_folder
import unittest

def _check(u, op):
    u.assertEqual(op.operationId, 'addPet')

class OperationAccessTestCase(unittest.TestCase):
    """ test for methods to access Operation """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which='wordnik'))

    def test_resolve(self):
        """
        """
        _check(self, self.app.resolve(utils.jp_compose(['#', 'paths', '/pet', 'post'])))

    def test_cascade_resolve(self):
        """
        """
        path = self.app.resolve(utils.jp_compose(['#', 'paths', '/pet']))

        _check(self, path.resolve('post'))
        _check(self, path.post)

    def test_tag_operationId(self):
        """
        """
        _check(self, self.app.op['pet', 'addPet'])
        _check(self, self.app.op['addPet'])

