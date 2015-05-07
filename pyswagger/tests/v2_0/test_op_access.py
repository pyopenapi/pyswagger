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

    def test_shortcut(self):
        """
        """
        _check(self, self.app.s('/pet').post)
        _check(self, self.app.s('/pet', b=SwaggerApp._shortcut_[SwaggerApp.sc_path]).post)
        _check(self, self.app.s('pet').post)
        _check(self, self.app.s('pet', b=SwaggerApp._shortcut_[SwaggerApp.sc_path]).post)

    def test_special_char(self):
        """ when the path has '{' and '}' """
        self.assertEqual(
                self.app.resolve(utils.jp_compose(['#', 'paths', '/user/{username}'])).get.operationId,
                'getUserByName'
        )
