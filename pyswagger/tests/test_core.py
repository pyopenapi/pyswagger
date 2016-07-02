from pyswagger import App, utils
from .utils import get_test_data_folder
from pyswagger.spec.base import BaseObj
import pyswagger
import unittest
import httpretty
import os
import six


class SwaggerCoreTestCase(unittest.TestCase):
    """ test core part """

    def test_backward_compatible_v1_2(self):
        """ make sure alias works """
        self.assertEqual(pyswagger.SwaggerAuth, pyswagger.Security)
        self.assertEqual(pyswagger.App._create_, pyswagger.App.create)

    @httpretty.activate
    def test_auto_schemes(self):
        """ make sure we scheme of url to access
        swagger.json as default scheme
        """
        # load swagger.json
        data = None
        with open(os.path.join(get_test_data_folder(
                version='2.0',
                which=os.path.join('schema', 'model')
                ), 'swagger.json')) as f:
            data = f.read()

        httpretty.register_uri(
            httpretty.GET,
            'http://test.com/api-doc/swagger.json',
            body=data
        )

        app = App._create_('http://test.com/api-doc/swagger.json')
        self.assertEqual(app.schemes, ['http'])

    @httpretty.activate
    def test_load_from_url_without_file(self):
        """ try to load from a url withou swagger.json """
        data = None
        with open(os.path.join(get_test_data_folder(
            version='2.0',
            which='wordnik'), 'swagger.json')) as f:
            data = f.read()

        httpretty.register_uri(
            httpretty.GET,
            'http://10.0.0.10:8080/swaggerapi/api/v1beta2',
            body=data
        )

        # no exception should be raised
        app = App.create('http://10.0.0.10:8080/swaggerapi/api/v1beta2')
        self.assertTrue(app.schemes, ['http'])
        self.assertTrue(isinstance(app.root, BaseObj))

    def test_no_host_basePath(self):
        """ test case for swagger.json without
        'host' and 'basePath' defined
        """
        path = get_test_data_folder(
            version='2.0',
            which=os.path.join('patch', 'no_host_schemes')
        )
        fu = utils.normalize_url(path) # file uri version of path

        # load swagger.json from a file path
        app = App.create(path)
        req, _ = app.s('t1').get()
        self.assertEqual(req.url, '//localhost/t1')
        self.assertEqual(req.schemes, ['file'])
        req.prepare(scheme='file', handle_files=False)
        self.assertEqual(req.url, 'file://localhost/t1')

        # load swagger.json from a file uri
        self.assertNotEqual(six.moves.urllib.parse.urlparse(fu).scheme, '')
        app = App.create(fu)
        req, _ = app.s('t1').get()
        self.assertEqual(req.url, '//localhost/t1')
        self.assertEqual(req.schemes, ['file'])
        req.prepare(scheme='file', handle_files=False)
        self.assertEqual(req.url, 'file://localhost/t1')

        # load swagger.json from a remote uri
        def _hook(url):
            # no matter what url, return the path of local swagger.json
            return fu

        url = 'test.com/api/v1'
        app = App.load('https://'+url, url_load_hook=_hook)
        app.prepare()
        # try to make a Request and verify its url
        req, _ = app.s('t1').get()
        self.assertEqual(req.url, '//test.com/t1')
        self.assertEqual(req.schemes, ['https'])
        req.prepare(scheme='https', handle_files=False)
        self.assertEqual(req.url, 'https://test.com/t1')

