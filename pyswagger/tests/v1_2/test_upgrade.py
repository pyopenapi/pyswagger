from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik'))


class Swagger_Upgrade_TestCase(unittest.TestCase):
    """ test for upgrade from converting 1.2 to 2.0 """

    def test_resource_list(self):
        """
        """

    def test_resource(self):
        """
        """

    def test_operation(self):
        """
        """

    def test_authorization(self):
        """
        """

    def test_parameter(self):
        """
        """

    def test_model(self):
        """
        """

