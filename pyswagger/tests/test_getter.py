from pyswagger import SwaggerApp
from .utils import get_test_data_folder
import unittest
import os


class GetterTestCase(unittest.TestCase):
    """ test getter """

    def test_random_name_v2_0(self):
        """
        """
        path = get_test_data_folder(
            version='2.0',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')
        # should not raise ValueError
        app = SwaggerApp.create(path)

    def test_random_name_v1_2(self):
        """
        """
        path = get_test_data_folder(
            version='1.2',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')
         # should not raise ValueError
        app = SwaggerApp.create(path)
