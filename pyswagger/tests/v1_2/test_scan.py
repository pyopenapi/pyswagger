from pyswagger import SwaggerApp
from pyswagger.scan import Scanner, Dispatcher
from ..utils import get_test_data_folder
from pyswagger.spec.v1_2.objects import (
    Resource,
    Authorization,
    Operation,
    ResponseMessage,
    Parameter
)
import unittest
import weakref


class CountObject(object):
    """ a scanner for counting objects and looking for
    longest attribute name. Just for test.
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.total = {
            Resource: 0,
            Authorization: 0,
            Operation: 0,
            ResponseMessage: 0
        }
        self.long_name = ''

    @Disp.register([Resource, Authorization, Operation, ResponseMessage])
    def _count(self, path, obj, _):
        self.total[obj.__class__] = self.total[obj.__class__] + 1
        return path.rsplit('/', 1)[1]

    @Disp.result
    def _result(self, name):
        if len(name) > len(self.long_name):
            self.long_name = name


class PathRecord(object):
    """ a scanner to record all json path
    """

    class Disp(Dispatcher): pass

    def __init__(self):
        self.resource = []
        self.authorization = []
        self.response_message = []
        self.parameter = []

    @Disp.register([Resource])
    def _resource(self, path, obj, _):
        self.resource.append(path)        

    @Disp.register([Authorization])
    def _authorization(self, path, obj, _):
        self.authorization.append(path) 

    @Disp.register([ResponseMessage])
    def _response_message(self, path, obj, _):
        if path.startswith('#/apis/store'):
            self.response_message.append(path)

    @Disp.register([Parameter])
    def _parameter(self, path, obj, _):
        if path.startswith('#/apis/pet/apis/updatePetWithForm'):
            self.parameter.append(path)


app = SwaggerApp.load(get_test_data_folder(version='1.2', which='wordnik')) 


class ScannerTestCase(unittest.TestCase):
    """ test scanner """
    def test_count(self):
        s = Scanner(app)
        co = CountObject()
        s.scan(route=[co], root=app.raw)

        self.assertEqual(co.long_name, 'createUsersWithArrayInput')
        self.assertEqual(co.total, {
            Authorization: 1,
            Resource: 3,
            Operation: 20,
            ResponseMessage: 23
        })

    def test_leaves(self):
        s = Scanner(app)
        co = CountObject()
        s.scan(route=[co], root=app.raw, leaves=[Operation])
        # the scanning would stop at Operation, so ResponseMessage
        # would not be counted.
        self.assertEqual(co.total, {
            Authorization: 1,
            Resource: 3,
            Operation: 20,
            ResponseMessage: 0
        })


    def test_path(self):
        self.maxDiff = None
        s = Scanner(app)
        p = PathRecord()
        s.scan(route=[p], root=app.raw)

        self.assertEqual(sorted(p.resource), sorted(['#/apis/store', '#/apis/user', '#/apis/pet']))
        self.assertEqual(p.authorization, ['#/authorizations/oauth2'])
        self.assertEqual(sorted(p.response_message), sorted([
            '#/apis/store/apis/placeOrder/responseMessages/0',
            '#/apis/store/apis/deleteOrder/responseMessages/1',
            '#/apis/store/apis/deleteOrder/responseMessages/0',
            '#/apis/store/apis/getOrderById/responseMessages/1',
            '#/apis/store/apis/getOrderById/responseMessages/0'
        ]))
        self.assertEqual(len(p.parameter), 3)


class ResolveTestCase(unittest.TestCase):
    """ test for scanner: Resolve """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='model_subtypes')) 
        
    def test_ref_resolve(self):
        """ make sure pre resolve works """
        ref = getattr(self.app.resolve('#/definitions/user!##!UserWithInfo').allOf[0], 'ref_obj')
        self.assertTrue(isinstance(ref, weakref.ProxyTypes))
        self.assertEqual(ref, self.app.resolve('#/definitions/user!##!User'))

