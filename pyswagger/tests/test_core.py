import pyswagger
import unittest


class SwaggerCoreTestCase(unittest.TestCase):
    """ test core part """

    def test_auth_security(self):
        """ make sure alias works """
        self.assertEqual(pyswagger.SwaggerAuth, pyswagger.SwaggerSecurity)

