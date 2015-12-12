from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest


class BitBucketTestCase(unittest.TestCase):
    """ test for bitbucket related """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.load(get_test_data_folder(
            version='2.0',
            which='bitbucket'
        ))

        # bypass cyclic testing
        kls.app.prepare(strict=False)

    def test_load(self):
        # make sure loading is fine,
        # this test case could be removed when something else exists in this suite.
        pass
