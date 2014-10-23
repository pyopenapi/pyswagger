from pyswagger import SwaggerApp
from pyswagger.scan import Scanner, Dispatcher
from ..utils import get_test_data_folder
from pyswagger.spec.v1_2.objects import (
    Resource,
    Authorization,
    Operation
)
import unittest


class CountObject(object):
    """ a scanner for counting objects and looking for
    longest attribute name. Just for test.
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.total = {
            Resource: 0,
            Authorization: 0,
            Operation: 0
        }
        self.long_name = ''

    @Disp.register([Resource, Authorization, Operation])
    def _count(self, scope, name, obj, _):
        self.total[obj.__class__] = self.total[obj.__class__] + 1        
        return name

    @Disp.result
    def _result(self, name):
        if len(name) > len(self.long_name):
            self.long_name = name


app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 


class ScannerTestCase(unittest.TestCase):
    """ test scanner """
    def test_count(self):
        s = Scanner(app)
        co = CountObject()
        s.scan(route=[co])

        self.assertEqual(co.long_name, 'createUsersWithArrayInput')
        self.assertEqual(co.total, {
            Authorization: 1,
            Resource: 3,
            Operation: 20
        })

