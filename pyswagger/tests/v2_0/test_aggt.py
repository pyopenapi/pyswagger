from pyswagger import SwaggerApp
from pyswagger.errs import CycleDetectionError
from ..utils import get_test_data_folder
import unittest
import os


class AggregateTestCase(unittest.TestCase):
    """ test aggt.py """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(
            version='2.0',
            which='aggt'
        ))

    def test_array_combine(self):
        """ make sure properties scattered into multiple
        Schema(s) could be aggregated.
        """
        s1 = self.app.resolve('#/definitions/s1').final
        self.assertEqual(10, s1.maxItems)
        self.assertEqual(5, s1.minItems)
        self.assertEqual('string', getattr(s1.items, 'type'))
        self.assertEqual('array', getattr(s1, 'type'))
        self.assertEqual(sorted(s1.required), sorted(["a", "b", "c", "d"]))
        self.assertEqual(sorted(s1.enum), sorted(["a", "b", "c", "d"]))

    def test_object_properties_merge(self):
        """ Schema.properties should be merged """
        s2 = self.app.resolve('#/definitions/s2').final
        self.assertEqual('object', getattr(s2, 'type'))
        self.assertTrue('password' in s2.properties, 'should has password')
        self.assertTrue('age' in s2.properties, 'should has age')
        self.assertEqual('string', getattr(s2.properties['password'], 'type'))
        self.assertTrue('address' in s2.properties, 'should has address')
        self.assertTrue('major' in s2.properties, 'should has major')

    def test_cycle_detection(self):
        """ cyclic reference should be detected
        """
        self.assertRaises(CycleDetectionError, SwaggerApp._create_, get_test_data_folder(
            version='2.0',
            which=os.path.join('aggt', 'circular')
        ))

    def test_schema_allof_with_ref(self):
        """ allOf composite with '$ref'
        """
        s3 = self.app.resolve('#/definitions/s3').final
        self.assertTrue('name' in s3.properties, 'should has name')
        self.assertTrue('age' in s3.properties, 'should has age')
        self.assertTrue('phone' in s3.properties, 'should has phone')

    def test_schema_allof_with_items(self):
        """ make sure items is correctly merged
        """
        s4 = self.app.resolve('#/definitions/s4').final
        self.assertEqual('integer', s4.items.final.type)
        self.assertEqual('int32', s4.items.final.format)

