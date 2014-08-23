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

