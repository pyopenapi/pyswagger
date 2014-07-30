from pyswagger import SwaggerApp
from .utils import get_test_data_folder
import unittest


class PropertyTestCase(unittest.TestCase):
    """ basic usage, used during development """
    def setUp(self):
        self.app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))

    def test_info(self):
        """ Info Object """
        self.assertTrue(hasattr(self.app, 'info'))

