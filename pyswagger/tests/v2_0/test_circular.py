from pyswagger import SwaggerApp, utils, primitives, errs
from ..utils import get_test_data_folder
from ...scanner import CycleDetector 
from ...scan import Scanner
import unittest
import os
import six


class CircularRefTestCase(unittest.TestCase):
    """ test for circular reference guard """

    def test_path_item_prepare_with_cycle(self):
        app = SwaggerApp.load(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'path_item')
        ))

        # should raise nothing
        app.prepare()

    def test_path_item(self):
        folder = get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'path_item')
        )

        def _pf(s):
            return six.moves.urllib.parse.urlunparse((
                'file',
                '',
                folder,
                '',
                '',
                s))

        app = SwaggerApp.create(folder)
        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.assertEqual(sorted(c.cycles['path_item']), sorted([[
            _pf('/paths/~1p1'),
            _pf('/paths/~1p2'),
            _pf('/paths/~1p3'),
            _pf('/paths/~1p4'),
            _pf('/paths/~1p1')
        ]]))

    def test_schema(self):
        folder = get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema')
        )

        def _pf(s):
            return six.moves.urllib.parse.urlunparse((
                'file',
                '',
                folder,
                '',
                '',
                s))


        app = SwaggerApp.load(folder)
        app.prepare(strict=False)

        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.maxDiff = None
        self.assertEqual(sorted(c.cycles['schema']), sorted([
            [_pf('/definitions/s10'), _pf('/definitions/s11'), _pf('/definitions/s9'), _pf('/definitions/s10')],
            [_pf('/definitions/s5'), _pf('/definitions/s5')],
            [_pf('/definitions/s1'), _pf('/definitions/s2'), _pf('/definitions/s3'), _pf('/definitions/s4'), _pf('/definitions/s1')],
            [_pf('/definitions/s12'), _pf('/definitions/s13'), _pf('/definitions/s12')],
            [_pf('/definitions/s6'), _pf('/definitions/s7'), _pf('/definitions/s6')],
            [_pf('/definitions/s14'), _pf('/definitions/s15'), _pf('/definitions/s14')]
        ]))

    def test_deref(self):
        app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema'),
            ),
            strict=False
        )

        s = app.resolve('#/definitions/s1')
        self.assertRaises(errs.CycleDetectionError, utils.deref, s)

    def test_primfactory(self):
        app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema'),
            ),
            strict=False
        )

        s = app.resolve('#/definitions/s1')
        self.assertRaises(errs.CycleDetectionError, primitives.prim_factory, s, {})
 
