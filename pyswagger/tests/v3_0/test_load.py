from pyswagger import App
from ..utils import get_test_file
from ...spec.v3_0.objects import OpenApi
import unittest
import os
import yaml


class Load_3_0_SpecTestCase(unittest.TestCase):
    """ test loading open-api 3.0 spec
    """

    def test_api_with_examples(self):
        """ load api-with-examples.yaml
        """
        oai = OpenApi(
            yaml.load(get_test_file(version='3.0', which='open_api', file_name='api-with-examples.yaml')),
            path='#'
        )

    def test_petstore_expanded(self):
        """ load petstore-expanded.yaml
        """
        oai = OpenApi(
            yaml.load(get_test_file(version='3.0', which='open_api', file_name='petstore-expanded.yaml')),
            path='#'
        )

    def test_petstore(self):
        """ load pestore.yaml
        """
        oai = OpenApi(
            yaml.load(get_test_file(version='3.0', which='open_api', file_name='petstore.yaml')),
            path='#'
        )

    def test_uber(self):
        """ load uber.yaml
        """
        oai = OpenApi(
            yaml.load(get_test_file(version='3.0', which='open_api', file_name='uber.yaml')),
            path='#'
        )

