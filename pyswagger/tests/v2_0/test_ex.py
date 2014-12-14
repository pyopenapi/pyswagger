from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest
import os
import six


folder = get_test_data_folder(version='2.0', which='ex')


def _hook(url):
    global folder

    p = six.moves.urllib.parse.urlparse(url)
    if p.scheme != 'file':
        return url

    path = os.path.join(folder, p.path if not p.path.startswith('/') else p.path[1:])
    return six.moves.urllib.parse.urlunparse(p[:2]+(path,)+p[3:])


class ExternalDocumentTestCase(unittest.TestCase):
    """ test case for external document """

    @classmethod
    def setUpClass(kls):
        global folder

        kls.app = SwaggerApp.load(
            url='file:///root/swagger.json',
            url_load_hook=_hook
        )
        kls.app.prepare()

    def test_resolve(self):
        """ make sure resolve with full JSON reference
        is the same as resolve with JSON pointer.
        """
        p = self.app.resolve('#/paths/~1full')
        p_ = self.app.resolve('file:///root/swagger.json#/paths/~1full')
        # refer to 
        #      http://stackoverflow.com/questions/10246116/python-dereferencing-weakproxy 
        # for how to dereferencing weakref
        self.assertEqual(p.__repr__(), p_.__repr__())

    def test_full_path_item(self):
        """ make sure PathItem is correctly merged
        """
        p = self.app.resolve('#/paths/~1full')
        self.assertNotEqual(p.get, None)
        self.assertTrue('default' in p.get.responses)
        self.assertTrue('404' in p.get.responses)

        another_p = self.app.resolve('file:///full/swagger.json#/paths/~1user')
        self.assertNotEqual(id(p), id(another_p))
        self.assertTrue('default' in another_p.get.responses)
        self.assertTrue('404' in another_p.get.responses)

    def test_full_path_item_url(self):
        """ make sure url is correctly patched
        """
        p = self.app.resolve('#/paths/~1full')
        self.assertEqual(p.get.url, 'test.com/v1/full')

        original_p = self.app.resolve('file:///full/swagger.json#/paths/~1user')
        self.assertEqual(original_p.get.url, 'test1.com/v2/user')

    def test_partial_path_item(self):
        """ make sure partial swagger.json with PathItem
        loaded correctly.
        """
        p = self.app.resolve('#/paths/~1partial')
        self.assertEqual(p.get.url, 'test.com/v1/partial')

        original_p = self.app.resolve('file:///partial/path_item/swagger.json')        
        self.assertEqual(original_p.get.url, None)

    def test_partial_schema(self):
        """  make sure partial swagger.json with Schema
        loaded correctly.
        """
        p = self.app.resolve('#/definitions/s4')
        original_p = self.app.resolve('file:///partial/schema/swagger.json')

        # refer to 
        #      http://stackoverflow.com/questions/10246116/python-dereferencing-weakproxy 
        # for how to dereferencing weakref
        self.assertEqual(p.items.ref_obj.__repr__(), original_p.__repr__())

        p_ = self.app.resolve('#/definitions/s3')
        self.assertEqual(p_.__repr__(), original_p.items.ref_obj.__repr__())

