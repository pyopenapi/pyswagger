from pyswagger import App
from .utils import get_test_data_folder
import unittest

class BasicTestCase(unittest.TestCase):
    """ basic usage, used during development """
    def setUp(self):
        self.app = App(get_test_data_folder('basic'))

    def test_load_local(self):
        """ load local resource """
        self.assertEqual(1, 1)
