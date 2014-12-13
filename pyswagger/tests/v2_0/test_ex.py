from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
import unittest
import os
import six
import weakref


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
            url='root',
            url_load_hook=_hook
        )
        kls.app.prepare()

    def test_resolve(self):
        """ make sure resolve with full JSON reference
        is the same as resolve with JSON pointer.
        """
        p = self.app.resolve('#/paths/~1full')
        p_ = self.app.resolve('file:///root#/paths/~1full')
        # refer to 
        #      http://stackoverflow.com/questions/10246116/python-dereferencing-weakproxy 
        # for how to dereferencing weakref
        self.assertEqual(p.__repr__(), p_.__repr__())

    def test_path_item(self):
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

    def test_path_item_url(self):
        """ make sure url is correctly patched
        """
        p = self.app.resolve('#/paths/~1full')
        self.assertEqual(p.get.url, 'test.com/v1/full')

        another_p = self.app.resolve('file:///full/swagger.json#/paths/~1user')
        self.assertEqual(another_p.get.url, 'test1.com/v2/user')

