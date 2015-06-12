from pyswagger import utils, errs
from datetime import datetime
import unittest
import functools
import six


class SwaggerUtilsTestCase(unittest.TestCase):
    """ test iso 8601 converter """

    def test_iso8601_convert_from_string(self):
        """ convert string to date/datetime """
        self.assertEqual(utils.from_iso8601('2007-04-05'), datetime(2007, 4, 5))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30'), datetime(2007, 4, 5, 14, 30))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30Z'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30:00-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))

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

    def test_jr_split(self):
        """ test jr_split """
        self.assertEqual(utils.jr_split(
            'http://test.com/api/swagger.json#/definitions/s1'), (
            'http://test.com/api/swagger.json', '#/definitions/s1'))
        self.assertEqual(utils.jr_split(
            'http://test/com/api/'), (
            'http://test/com/api/', '#'))
        self.assertEqual(utils.jr_split(
            '#/definitions/s1'), (
            '', '#/definitions/s1'))
        self.assertEqual(utils.jr_split(
            '/user/tmp/local/ttt'), (
            'file:///user/tmp/local/ttt', '#'))
        self.assertEqual(utils.jr_split(
            '/user/tmp/local/ttt/'), (
            'file:///user/tmp/local/ttt', '#'))
        # relative path should be converted to absolute one
        self.assertEqual(utils.jr_split(
            'user'), (
            utils.normalize_url('user'), '#'))
        self.assertEqual(utils.jr_split(
            '#'), (
            '', '#'))
        self.assertEqual(utils.jr_split(
            '//'), (
            '', '#'))

    def test_cycle_guard(self):
        def my_id(obj):
            return obj

        c = utils.CycleGuard(identity_hook=my_id)
        c.update(1)
        self.assertRaises(errs.CycleDetectionError, c.update, 1)

    def test_normalize_url(self):
        self.assertEqual(utils.normalize_url(None), None)
        self.assertEqual(utils.normalize_url(''), '')
        self.assertEqual(utils.normalize_url('http://test.com/a/q.php?q=100'), 'http://test.com/a/q.php?q=100')
        self.assertEqual(utils.normalize_url('/tmp/local/test/'), 'file:///tmp/local/test')
        self.assertEqual(utils.normalize_url('/tmp/local/test'), 'file:///tmp/local/test')
        self.assertEqual(utils.normalize_url('/tmp/local/test in space.txt'), 'file:///tmp/local/test%20in%20space.txt')

    def test_normalize_jr(self):
        self.assertEqual(utils.normalize_jr(None, ''), None)
        self.assertEqual(utils.normalize_jr('User', '#/definitions'), '#/definitions/User')
        self.assertEqual(utils.normalize_jr('User', '#/definitions', 'http://test.com/api'), 'http://test.com/api#/definitions/User')
        self.assertEqual(utils.normalize_jr('#/definitions/User', '#/definitions', 'http://test.com/api'), 'http://test.com/api#/definitions/User')
        self.assertEqual(utils.normalize_jr(
            'http://test.com/api#/definitions/User', ''),
            'http://test.com/api#/definitions/User'
        )

    def test_get_swagger_version(self):
        self.assertEqual(utils.get_swagger_version({'swaggerVersion': '1.2'}), '1.2')
        self.assertEqual(utils.get_swagger_version({'swagger': '2.0'}), '2.0')
        self.assertEqual(utils.get_swagger_version({'qq': '20.0'}), None)

    def test_diff(self):
        dict1 = dict(a=1, b=[1, 2, 3])
        dict2 = dict(a=1, b=[1, 3])
        dict3 = dict(
            a=dict(a=1, b=[1, 2, 3], c=4),
            b=dict(a=2, b=[1, 2, 3], c=4),
        )
        dict4 = dict(
            a=dict(a=2, b=[1, 3], c=5),
            b=dict(a=2, b=[1, 2], c=4),
        )

        list1 = [dict1, dict3]
        list2 = [dict2, dict4]

        self.assertEqual(utils._diff_(dict1, dict2), [
            ('b', 3, 2),
        ])

        self.assertEqual(utils._diff_(dict2, dict1), [
            ('b', 2, 3),
        ])

        self.assertEqual(sorted(utils._diff_(dict3, dict4)), sorted([
            ('a/a', 1, 2), ('a/b', 3, 2), ('a/c', 4, 5), ('b/b', 3, 2)
        ]))

        self.assertEqual(sorted(utils._diff_(list1, list2)), sorted([
            ('0/b', 3, 2),
            ('1/a/a', 1, 2),
            ('1/a/b', 3, 2),
            ('1/a/c', 4, 5),
            ('1/b/b', 3, 2)
        ]))

        # test include
        self.assertEqual(sorted(utils._diff_(dict3, dict4, include=['a'])), sorted([
            ('a/a', 1, 2), ('a/b', 3, 2), ('a/c', 4, 5)
        ]))
        # test exclude
        self.assertEqual(sorted(utils._diff_(dict3, dict4, exclude=['a'])), sorted([
            ('b/b', 3, 2)
        ]))
        # test include and exclude
        self.assertEqual(sorted(utils._diff_(dict3, dict4, include=['a', 'b'], exclude=['a'])), sorted([
            ('b/b', 3, 2)
        ]))

    def test_get_or_none(self):
        """ test for get_or_none
        """
        class A(object): pass
        a = A()
        setattr(A, 'b', A())
        setattr(a.b, 'c', A())
        setattr(a.b.c, 'd', 'test string')
        self.assertEqual(utils.get_or_none(a, 'b', 'c', 'd'), 'test string')
        self.assertEqual(utils.get_or_none(a, 'b', 'c', 'd', 'e'), None)


class WalkTestCase(unittest.TestCase):
    """ test for walk """

    @staticmethod
    def _out(conf, idx):
        return conf[idx]

    def test_self_cycle(self):
        conf = {
            0: [0]
        }

        cyc = utils.walk(
            0, functools.partial(WalkTestCase._out, conf)
        )
        self.assertEqual(cyc, [[0, 0]])

    def test_1_long_cycle(self):
        conf = {
            0: [1],
            1: [2],
            2: [3],
            3: [4],
            4: [5],
            5: [1]
        }

        cyc = []
        for i in range(6):
            cyc = utils.walk(
                i,
                functools.partial(WalkTestCase._out, conf),
                cyc
            )

        self.assertEqual(cyc, [[1, 2, 3, 4, 5, 1]])

    def test_multiple_cycles(self):
        conf = {
            0: [6],
            1: [6],
            2: [0],
            3: [1],
            4: [4],
            5: [3],
            6: [3],
            7: [4],
            8: [0]
        }

        cyc = []
        for i in range(9):
            cyc = utils.walk(
                i,
                functools.partial(WalkTestCase._out, conf),
                cyc
            )

        self.assertEqual(cyc, [
            [1, 6, 3, 1],
            [4, 4]
            ])

    def test_cycles_share_border(self):
        conf = {
            0: [1],
            1: [2],
            2: [3],
            3: [0, 5],
            4: [2],
            5: [4]
        }

        cyc = []
        for i in range(6):
            cyc = utils.walk(
                i,
                functools.partial(WalkTestCase._out, conf),
                cyc
            )

        self.assertEqual(cyc, [
            [0, 1, 2, 3, 0],
            [2, 3, 5, 4, 2]
            ])

    def test_no_cycle(self):
        conf = {
            0: [1, 2],
            1: [2, 3],
            2: [3, 4],
            3: [4, 5],
            4: [5, 6],
            5: [6, 7],
            6: [7],
            7: []
        }

        cyc = []
        for i in range(8):
            cyc = utils.walk(
                i,
                functools.partial(WalkTestCase._out, conf),
                cyc
            )

        self.assertEqual(cyc, [])

    def test_multiple_cycles_2(self):
        conf = {
            0: [1, 4],
            1: [2],
            2: [0, 3],
            3: [4, 5],
            4: [1, 2],
            5: [4]
        }

        cyc = []
        for i in range(6):
            cyc = utils.walk(
                i,
                functools.partial(WalkTestCase._out, conf),
                cyc
            )

        self.assertEqual(sorted(cyc), sorted([
            [0, 1, 2, 0],
            [0, 4, 1, 2, 0],
            [0, 4, 2, 0],
            [1, 2, 3, 4, 1],
            [1, 2, 3, 5, 4, 1],
            [2, 3, 5, 4, 2],
            [2, 3 ,4, 2]
            ]))


