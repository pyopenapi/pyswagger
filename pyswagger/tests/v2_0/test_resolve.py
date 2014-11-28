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
