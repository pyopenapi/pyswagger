from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
from ...scanner import CycleDetector 
from ...scan import Scanner
import unittest
import os


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
        app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'path_item')
        ))
        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.assertEqual(sorted(c.cycles['path_item']), sorted([[
            '#/paths/~1p1',
            '#/paths/~1p2',
            '#/paths/~1p3',
            '#/paths/~1p4',
            '#/paths/~1p1'
        ]]))

    def test_schema(self):
        app = SwaggerApp.load(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema')
        ))
        app.prepare(strict=False)

        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.maxDiff = None
        self.assertEqual(sorted(c.cycles['schema']), sorted([
            ['#/definitions/s10', '#/definitions/s11', '#/definitions/s9', '#/definitions/s10'],
            ['#/definitions/s5', '#/definitions/s5'],
            ['#/definitions/s1', '#/definitions/s2', '#/definitions/s3', '#/definitions/s4', '#/definitions/s1'],
            ['#/definitions/s12', '#/definitions/s13', '#/definitions/s12'],
            ['#/definitions/s6', '#/definitions/s7', '#/definitions/s6'],
            ['#/definitions/s14', '#/definitions/s15', '#/definitions/s14']
        ]))

