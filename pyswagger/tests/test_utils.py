from pyswagger import utils
from datetime import datetime
import unittest


class SwaggerUtilsTestCase(unittest.TestCase):
    """ test iso 8601 converter """

    def test_iso8601_convert_from_string(self):
        """ convert string to date/datetime """
        self.assertEqual(utils.from_iso8601('2007-04-05'), datetime(2007, 4, 5))
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

    def test_json_pointer(self):
        """ json pointer io function """
        self.assertEqual(utils.jp_compose('/test'), '~1test')
        self.assertEqual(utils.jp_compose('~test'), '~0test')
        self.assertEqual(utils.jp_compose('/~test'), '~1~0test')
        self.assertEqual(utils.jp_compose('a', 'b'), 'b/a')
        self.assertEqual(utils.jp_compose(''), '')
        self.assertEqual(utils.jp_compose(None, 'base'), 'base')

        cs = ['~test1', '/test2', 'test3']
        c = utils.jp_compose(cs, 'base')
        self.assertEqual(c, 'base/~0test1/~1test2/test3')
        self.assertEqual(utils.jp_split(c)[1:], cs)

        self.assertEqual(utils.jp_split('~1test'), ['/test'])
        self.assertEqual(utils.jp_split('~0test'), ['~test'])
        self.assertEqual(utils.jp_split('~1~0test'), ['/~test'])
        self.assertEqual(utils.jp_split(''), [])
        self.assertEqual(utils.jp_split(None), [])
        self.assertEqual(utils.jp_split('/~1~0test/qq/~0test/~1test/'), ['', '/~test', 'qq', '~test', '/test', ''])

    def test_scope_dict(self):
        """ ScopeDict """
        obj = {
            'a!b': 1,
            'c!d!ee': 2,
            'e!f!g': 3,
            'a!f!g': 4,
        }
        d = utils.ScopeDict(obj)
        d.sep = '!'
        self.assertEqual(d['a!b'], 1)
        self.assertEqual(d['b'], 1)
        self.assertEqual(d['ee'], 2)
        self.assertEqual(d['a', 'b'], 1)
        self.assertEqual(d['c', 'd', 'ee'], 2)
        self.assertEqual(d['d', 'ee'], 2)
        self.assertRaises(ValueError, d.__getitem__, ('f', 'g'))
        self.assertRaises(TypeError, lambda x: d.sep)

    def test_dict_to_tuple(self):
        """ get_dict_as_tuple """
        self.assertEqual(
            utils.get_dict_as_tuple({'a':'b'}),
            ('a', 'b')
        )

    def test_nv_tuple_list_replace(self):
        """ nv_tuple_list_replace """
        d = [
            (1, 1),
            (2, 2),
            (3, 3)
        ]

        utils.nv_tuple_list_replace(d, (1, 4))
        self.assertEqual(d, [
            (1, 4),
            (2, 2),
            (3, 3)
        ])

        utils.nv_tuple_list_replace(d, (4, 4))
        self.assertEqual(d, [
            (1, 4),
            (2, 2),
            (3, 3),
            (4, 4)
        ])

    def test_import_string(self):
        """ test import_string """
        self.assertEqual(utils.import_string('qoo_%^&%&'), None)
        self.assertNotEqual(utils.import_string('pyswagger'), None)

    def test_path2url(self):
        """ test path2url """
        self.assertEqual(utils.path2url('/opt/local/a.json'), 'file:///opt/local/a.json')

