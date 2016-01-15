from pyswagger import SwaggerApp
from ..utils import get_test_data_folder
from ...utils import deref, final
from ...spec.v2_0.parser import PathItemContext
import unittest
import os
import six


def _gen_hook(folder):
    def _hook(url):
        p = six.moves.urllib.parse.urlparse(url)
        if p.scheme != 'file':
            return url

        path = os.path.join(folder, p.path if not p.path.startswith('/') else p.path[1:])
        return six.moves.urllib.parse.urlunparse(p[:2]+(path,)+p[3:])

    return _hook


class ExternalDocumentTestCase(unittest.TestCase):
    """ test case for external document """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.load(
            url='file:///root/swagger.json',
            url_load_hook=_gen_hook(get_test_data_folder(version='2.0', which='ex'))
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

        another_p = self.app.resolve('file:///full/swagger.json#/paths/~1user', PathItemContext)
        self.assertNotEqual(id(p), id(another_p))
        self.assertTrue('default' in another_p.get.responses)
        self.assertTrue('404' in another_p.get.responses)

    def test_full_path_item_url(self):
        """ make sure url is correctly patched
        """
        p = self.app.resolve('#/paths/~1full')
        self.assertEqual(p.get.url, 'test.com/v1/full')

        # only root document would be patched, others are only loaded for reference
        original_p = self.app.resolve('file:///full/swagger.json#/paths/~1user', PathItemContext)
        self.assertEqual(original_p.get.url, None)

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

    def test_relative_path_item(self):
        """ make sure that relative file schema works
           https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#relative-schema-file-example
        """
        def chk(obj):
            self.assertEqual(obj.get.responses['default'].description, 'relative, path_item, get, response')
            self.assertEqual(obj.put.responses['default'].description, 'relative, path_item, put, response')

        chk(self.app.s('relative'))
        chk(self.app.resolve('file:///root/path_item.json'))

    def test_relative_schema(self):
        """ test case for issue#53,
        relative file, which root is a Schema Object
        """
        app = SwaggerApp.load(
            url='file:///relative/internal.yaml',
            url_load_hook=_gen_hook(get_test_data_folder(version='2.0', which='ex'))
        )
        app.prepare()


class ReuseTestCase(unittest.TestCase):
    """ test case for 'reuse', lots of partial swagger document
        https://github.com/OAI/OpenAPI-Specification/blob/master/guidelines/REUSE.md#guidelines-for-referencing
    """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.load(
            url='file:///reuse/swagger.json',
            url_load_hook=_gen_hook(get_test_data_folder(version='2.0', which='ex'))
        )
        kls.app.prepare()

    def test_relative_folder(self):
        """ make sure the url prepend on $ref should be
        derived from the path of current document
        """
        o = deref(self.app.resolve('#/definitions/QQ'))
        self.assertEqual(o.description, 'Another simple model')

    def test_relative_parameter(self):
        """ make sure parameter from relative $ref
        is correctly injected(merged) in 'final' field.
        """
        o = final(self.app.s('pets').get.parameters[0])
        self.assertEqual(o.description, 'Results to skip when paginating through a result set') 

    def test_relative_response(self):
        """ make sure response from relative $ref
        is correctly injected(merged) in 'final' field.
        """
        o = final(self.app.s('pets').get.responses['400'])
        self.assertEqual(o.description, 'Entity not found')

    def test_relative_path_item(self):
        """ make sure path-item from relative $ref
        is correctly injected(merged).
        """
        o1 = self.app.s('health').get
        self.assertEqual(o1.summary, 'Returns server health information')
        # make sure these objects are not referenced, but copied.
        o2 = self.app.resolve('file:///reuse/operations.json#/health')
        self.assertNotEqual(id(o1), id(o2), PathItemContext)

