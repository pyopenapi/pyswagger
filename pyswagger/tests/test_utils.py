from pyswagger import utils
from datetime import datetime
import unittest


class Iso8601TestCase(unittest.TestCase):
    """ test iso 8601 converter """

    def test_convert_from_string(self):
        """ convert string to date/datetime """
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30'), datetime(2007, 4, 5, 14, 30))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30Z'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30:00-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))

    def test_none_count(self):
        """ cound none value in dict """
        a = dict(a=None, b=None, c=1, d=None, e=2, f=None)
        self.assertEqual(4, utils.none_count(a))
        b = dict(a=1, b=2, c=3, d=4, e=5, f=6)
        self.assertEqual(0, utils.none_count(b))

