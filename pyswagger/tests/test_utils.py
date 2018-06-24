from pyswagger import utils, errs
from .utils import is_windows, is_py2
from datetime import datetime
import unittest
import functools
import six
import os


class SwaggerUtilsTestCase(unittest.TestCase):
    """ test iso 8601 converter """

    def test_iso8601_convert_from_string(self):
        """ convert string to date/datetime """
        self.assertEqual(utils.from_iso8601('2007-04-05'), datetime(2007, 4, 5))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30'), datetime(2007, 4, 5, 14, 30))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30Z'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T12:30:00-02:00'), datetime(2007, 4, 5, 14, 30, tzinfo=utils.FixedTZ(0, 0)))
        self.assertEqual(utils.from_iso8601('2007-04-05T00:00:00'), datetime(2007, 4, 5, 0, 0, 0))
        self.assertEqual(utils.from_iso8601('2007-04-05T00:00:00Z'), datetime(2007, 4, 5, 0, 0, 0, tzinfo=utils.FixedTZ(0, 0)))
        # microsecond
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.1'), datetime(2007, 4, 5, 14, 30, 24, 100000))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.11'), datetime(2007, 4, 5, 14, 30, 24, 110000))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.111'), datetime(2007, 4, 5, 14, 30, 24, 111000))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.1111'), datetime(2007, 4, 5, 14, 30, 24, 111100))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.11111'), datetime(2007, 4, 5, 14, 30, 24, 111110))
        self.assertEqual(utils.from_iso8601('2007-04-05T14:30:24.111111'), datetime(2007, 4, 5, 14, 30, 24, 111111))
        self.assertEqual(utils.from_iso8601('2016-08-05T03:14:14.809Z'), datetime(2016, 8, 5, 3, 14, 14, 809000, tzinfo=utils.FixedTZ(0, 0)))

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


    def test_derelativize_url(self):
        self.assertEquals(utils.derelativise_url('https://localhost/hurf/durf.json'), 'https://localhost/hurf/durf.json')
        self.assertEquals(utils.derelativise_url('https://localhost/hurf/./durf.json'), 'https://localhost/hurf/durf.json')
        self.assertEquals(utils.derelativise_url('https://localhost/hurf/../durf.json'), 'https://localhost/durf.json')
        self.assertEquals(utils.derelativise_url('https://localhost/hurf/.../durf.json'), 'https://localhost/durf.json')
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

        obj = {
            'tag1!##!get': 1,
            'tag2!##!something-get': 2,
        }
        d = utils.ScopeDict(obj)
        d.sep = '!##!'
        self.assertEqual(d['tag1', 'get'], 1)
        self.assertEqual(d['tag2', 'something-get'], 2)
        self.assertEqual(d['get'], 1)
        self.assertEqual(d['something-get'], 2)

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

    @unittest.skipUnless(not is_windows(), 'make no sense on windows')
    def test_path2url_on_unix(self):
        """ test path2url """
        self.assertEqual(utils.path2url('/opt/local/a.json'), 'file:///opt/local/a.json')

    @unittest.skipUnless(is_windows(), 'make no sense on unix')
    def test_path2url_on_windows(self):
        """ test path2url on windows """
        self.assertEqual(utils.path2url(r'C:\opt\local\a.json'), 'file:///C:/opt/local/a.json')

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

    @unittest.skipUnless(not is_windows(), 'make no sense on windows')
    def test_jr_split_on_unix(self):
        """ test jr_split on unix-like os """
        self.assertEqual(utils.jr_split(
            '/user/tmp/local/ttt'), (
            'file:///user/tmp/local/ttt', '#'))
        self.assertEqual(utils.jr_split(
            '/user/tmp/local/ttt/'), (
            'file:///user/tmp/local/ttt', '#'))

    @unittest.skipUnless(is_windows(), 'make no sense on unix')
    def test_jr_split_on_windows(self):
        """ test jr_split on windows """
        target = 'file:///C:/user/tmp/local/ttt' if is_py2() else 'file:///c:/user/tmp/local/ttt'

        self.assertEqual(utils.jr_split(r'C:\user\tmp\local\ttt'), (target, '#'))
        self.assertEqual(utils.jr_split(
            # check here for adding backslach at the end of raw string
            #   https://pythonconquerstheuniverse.wordpress.com/2008/06/04/gotcha-%E2%80%94-backslashes-in-windows-filenames/
            os.path.normpath('C:/user/tmp/local/ttt/')
            ), (target, '#'))

    def test_cycle_guard(self):
        c = utils.CycleGuard()
        c.update(1)
        self.assertRaises(errs.CycleDetectionError, c.update, 1)

    @unittest.skipUnless(not is_windows(), 'make no sense on windows')
    def test_normalize_url(self):
        self.assertEqual(utils.normalize_url(None), None)
        self.assertEqual(utils.normalize_url(''), '')
        self.assertEqual(utils.normalize_url('http://test.com/a/q.php?q=100'), 'http://test.com/a/q.php?q=100')
        self.assertEqual(utils.normalize_url('/tmp/local/test/'), 'file:///tmp/local/test')
        self.assertEqual(utils.normalize_url('/tmp/local/test'), 'file:///tmp/local/test')
        self.assertEqual(utils.normalize_url('/tmp/local/test in space.txt'), 'file:///tmp/local/test%20in%20space.txt')

    @unittest.skipUnless(is_windows(), 'make no sense on unix')
    def test_normalize_url_on_windows(self):
        self.assertEqual(utils.normalize_url(r'C:\path\to\something'), 'file:///C:/path/to/something')

    def test_normalize_jr(self):
        self.assertEqual(utils.normalize_jr(None), None)
        self.assertEqual(utils.normalize_jr(None, 'http://test.com/api/swagger.json'), None)
        self.assertEqual(utils.normalize_jr('User.json', 'http://test.com/api/swagger.json'), 'http://test.com/api/User.json')
        self.assertEqual(utils.normalize_jr('definitions/User.json', 'http://test.com/api/swagger.json'), 'http://test.com/api/definitions/User.json')
        self.assertEqual(utils.normalize_jr('#/definitions/User', 'http://test.com/api/swagger.json'), 'http://test.com/api/swagger.json#/definitions/User')
        self.assertEqual(utils.normalize_jr('#/definitions/User'), '#/definitions/User')

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
            ('a/a', 1, 2)
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

    def test_url_dirname(self):
        """ test url_dirname
        """
        self.assertEqual(utils.url_dirname('https://localhost/test/swagger.json'), 'https://localhost/test')
        self.assertEqual(utils.url_dirname('https://localhost/test/'), 'https://localhost/test/')
        self.assertEqual(utils.url_dirname('https://localhost/test'), 'https://localhost/test')

    def test_url_join(self):
        """ test url_join
        """
        self.assertEqual(utils.url_join('https://localhost/test', 'swagger.json'), 'https://localhost/test/swagger.json')
        self.assertEqual(utils.url_join('https://localhost/test/', 'swagger.json'), 'https://localhost/test/swagger.json')

    @unittest.skipUnless(not is_windows(), 'make no sense on windows')
    def test_patch_path(self):
        """ make sure patch_path works
        """
        self.assertEqual(utils.patch_path(
            '/Users/sudeep.agarwal/src/squiddy/api/v0.1',
            '/Users/sudeep.agarwal/src/squiddy/api/v0.1/swagger.yaml',
        ), '/Users/sudeep.agarwal/src/squiddy/api/v0.1/swagger.yaml')

    @unittest.skipUnless(is_windows(), 'make no sense on unix-like os')
    def test_patch_path_on_windows(self):
        self.assertEqual(utils.patch_path(
            'Users/sudeep.agarwal/src/squiddy/api/v0.1',
            'Users/sudeep.agarwal/src/squiddy/api/v0.1/swagger.yaml',
        ), 'Users/sudeep.agarwal/src/squiddy/api/v0.1/swagger.yaml')


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

    def test_case_insensitive_dict(self):
        """ test utils.CaseInsensitiveDict
        """
        normal = utils.CaseInsensitiveDict()
        normal['Content-Type'] = 'application/json'
        self.assertTrue('Content-Type' in normal)
        self.assertTrue('content-type' in normal)
        self.assertEqual(normal['content-type'], 'application/json')

        # test iteration
        for k, v in normal.iteritems():
            self.assertEqual(k, 'Content-Type')
            self.assertEqual(v, 'application/json')
            break
        else:
            # should not reach here
            self.assertTrue(False)

        for v in normal.itervalues():
            self.assertEqual(v, 'application/json')
            break
        else:
            # should not reach here
            self.assertTrue(False)
