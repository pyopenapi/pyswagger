from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest
import os


class ValidationTestCase(unittest.TestCase):
    """ test validation of 2.0 spec """

    def test_read_only_and_required(self):
        """ a property is both read-only and required """
        app = SwaggerApp.load(get_test_data_folder(
            version='2.0',
            which=os.path.join('validate', 'req_and_readonly')
        ))
        errs = app.validate(strict=False)
        self.maxDiff = None
        self.assertEqual(sorted(errs), sorted([
            ((u'#/definitions/ReadOnly', 'Schema'), 'ReadOnly property in required list: protected')
        ]))
