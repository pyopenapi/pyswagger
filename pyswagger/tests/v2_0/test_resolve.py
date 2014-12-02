from pyswagger import SwaggerApp, utils                                        
from pyswagger.spec.v2_0 import objects                                        
from ..utils import get_test_data_folder                                       
import unittest                                                                
import os                                                                      


class ResolvePathItemTestCase(unittest.TestCase):                              
    """ test for PathItem $ref """                                                 

    @classmethod                                                                   
    def setUpClass(kls):                                                           
        kls.app = SwaggerApp._create_(get_test_data_folder(                            
            version='2.0',                                                                 
            which=os.path.join('resolve', 'path_item')                                     
        ))                                                                             

    def test_path_item(self):                                                      
        """ make sure PathItem is correctly merged """
        a = self.app.resolve(utils.jp_compose('/a', '#/paths'))                        

        self.assertTrue(isinstance(a, objects.PathItem))     
        self.assertTrue(a.get.operationId, 'a.get')
        self.assertTrue(a.put.operationId, 'c.put')
        self.assertTrue(a.post.operationId, 'd.post')


class ResolveTestCase(unittest.TestCase):
    """ test for $ref other than PathItem """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(                            
            version='2.0',                                                                 
            which=os.path.join('resolve', 'other')                                     
        ))                                                                             

    def test_schema(self):
        """ make sure $ref to Schema works """
        p = self.app.s('/a').get

        self.assertEqual(id(p.parameters[1].schema.ref_obj), id(self.app.resolve('#/definitions/d1')))

    def test_parameter(self):
        """ make sure $ref to Parameter works """
        p = self.app.s('/a').get

        self.assertEqual(id(p.parameters[0].ref_obj), id(self.app.resolve('#/parameters/p1')))

    def test_response(self):
        """ make sure $ref to Response works """
        p = self.app.s('/a').get

        self.assertEqual(id(p.responses['default'].ref_obj), id(self.app.resolve('#/responses/r1')))

