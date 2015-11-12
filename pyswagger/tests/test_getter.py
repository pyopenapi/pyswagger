from pyswagger import SwaggerApp
from pyswagger.getter import UrlGetter
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

    def test_local_path_with_custome_getter(self):
        """ make sure path would be assigned when
        passing a getter class
        """
        cls = UrlGetter
        path = get_test_data_folder(
            version='2.0',
            which='random_file_name'
        )
        path = os.path.join(path, 'test_random.json')

        # should not raise errors
        app = SwaggerApp.load(path, getter=cls)
