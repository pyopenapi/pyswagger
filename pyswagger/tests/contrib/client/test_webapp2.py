from __future__ import absolute_import
from pyswagger import App
from pyswagger.contrib.client.webapp2 import Webapp2TestClient
from ...utils import create_pet_db, get_test_data_folder, pet_Mary
from webapp2_extras import sessions
import unittest
import webapp2
import json
import six
import sys
import os


pet_db = create_pet_db()
received_file = None
received_meta = None
received_headers = None

#
# a minimum webapp2 application for pet-store example
#

class PetStoreHandler(webapp2.RequestHandler):
    """
    """

    def pet(self):
        global pet_db
        global received_headers

        params = json.loads(self.request.body)
        if self.request.method == 'POST':
            if pet_db.read_(params['id']) != None:
                self.response.status_int = 409
            else:
                pet_db.create_(**params)
                self.response.status_int = 200
        elif self.request.method == 'PUT':
            received_headers = self.request.headers
            if not isinstance(params['id'], int):
                self.response.status_int = 400

            if not pet_db.update_(**params):
                self.response.status_int = 404
            else:
                self.response.status_int = 200
        else:
            self.response.status_int = 405

    def petById(self, pet_id):
        global pet_db

        if self.request.method == 'DELETE':
            if not pet_db.delete_(int(pet_id)):
                self.response.status_int = 400
            else:
                self.response.status_int = 200
        elif self.request.method == 'GET':
            pet = pet_db.read_(int(pet_id))
            if not pet:
                self.response.status_int = 404
            else:
                self.response.write(json.dumps(pet))
                self.response.status_int = 200
                self.response.content_type = 'application/json'
                self.response.content_type_params = {'charset': 'utf8'}
        else:
            self.response.status_int = 405

    def uploadFile(self):
        global received_file
        global received_meta

        f = self.request.POST['file']
        received_file = f.file.read()
        received_meta = self.request.get('additionalMetadata')


wapp = webapp2.WSGIApplication([
    webapp2.Route(r'/api/pet', handler=PetStoreHandler, handler_method='pet', methods=['POST', 'PUT']),
    webapp2.Route(r'/api/pet/<pet_id:\d+>', handler=PetStoreHandler, handler_method='petById', methods=['DELETE', 'GET']),
    webapp2.Route(r'/api/pet/uploadImage', handler=PetStoreHandler, handler_method='uploadFile', methods=['POST']),
])


cookie_cache = None


class CookieHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def getCookie(self):
        self.session['test_pyswagger'] = 'test 123'
        self.response.status_int = 200

    def keepCookie(self):
        global cookie_cache

        cookie_cache = self.session['test_pyswagger']
        self.response.status_int = 200


cookie_app = webapp2.WSGIApplication([
    webapp2.Route(r'/api/get_cookie', handler=CookieHandler, handler_method='getCookie', methods=['GET']),
    webapp2.Route(r'/api/keep_cookie', handler=CookieHandler, handler_method='keepCookie', methods=['GET']),
], config={
    'webapp2_extras.sessions': {
        'secret_key': 'key123',
        'cookie_args': {
            'max_age': 31557600, # one year
            'secure': False
        }
    }
})

@unittest.skipIf(sys.version_info[0] > 2, 'webapp2 only supports python 2.x')
class Webapp2TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='1.2',
            which='wordnik'
        ))

    def test_updatePet(self):
        global pet_db

        resp = Webapp2TestClient(wapp).request(
            self.app.op['updatePet'](body=dict(id=1, name='Tom1'))
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(1)['name'], 'Tom1')

    def test_reuse_req_and_resp(self):
        """ make sure reusing (req, resp) is fine """
        global pet_db

        cache = self.app.op['updatePet'](body=dict(id=1, name='Tom1'))
        resp = Webapp2TestClient(wapp).request(cache)
        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(1)['name'], 'Tom1')
        resp = Webapp2TestClient(wapp).request(cache)
        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(1)['name'], 'Tom1')

    def test_addPet(self):
        global pet_db

        resp = Webapp2TestClient(wapp).request(
            self.app.op['addPet'](body=dict(id=5, name='Mission')),
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(5)['name'], 'Mission')

    def test_deletePet(self):
        global pet_db

        resp = Webapp2TestClient(wapp).request(
            self.app.op['deletePet'](petId=5),
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(5), None)

    def test_getPetById(self):
        resp = Webapp2TestClient(wapp).request(
            self.app.op['getPetById'](petId=2),
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, pet_Mary)

    def test_uploadFile(self):
        global received_file
        global received_meta

        resp = Webapp2TestClient(wapp).request(
            self.app.op['uploadFile'](
                additionalMetadata='a test file', file=dict(data=six.BytesIO(six.b('a test Content')), filename='test.txt')
            ),
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(received_file.decode(), 'a test Content')
        self.assertEqual(received_meta, 'a test file')

    def test_cookie(self):
        global cookie_cache

        app = App.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('io', 'cookie')
        ))
        client = Webapp2TestClient(cookie_app, keep_cookie=True)
        resp = client.request(app.op['get_cookie']())
        self.assertEqual(resp.status, 200)

        resp = client.request(app.op['keep_cookie']())
        self.assertEqual(resp.status, 200)

        self.assertEqual(cookie_cache, 'test 123')

    def test_custom_headers(self):
        """ test customized headers """
        global received_headers

        resp = Webapp2TestClient(wapp).request(
            self.app.op['updatePet'](body=dict(id=1, name='Tom1')),
            headers={'X-TEST-HEADER': 'aaa'}
        )

        self.assertEqual(received_headers['X-TEST-HEADER'], 'aaa')

    def test_custom_headers_multiple_values_to_one_key(self):
        """ test customized headers with multiple values to one key """
        global received_headers

        resp = Webapp2TestClient(wapp).request(
            self.app.op['updatePet'](body=dict(id=1, name='Tom1')),
            headers=[('X-TEST-HEADER', 'aaa'), ('X-TEST-HEADER', 'bbb')]
        )
        self.assertEqual(received_headers['X-TEST-HEADER'], 'bbb')

        # with 'join_headers'
        resp = Webapp2TestClient(wapp).request(
            self.app.op['updatePet'](body=dict(id=1, name='Tom1')),
            headers=[('X-TEST-HEADER', 'aaa'), ('X-TEST-HEADER', 'bbb')],
            opt={'join_headers': True}
        )
        self.assertEqual(received_headers['X-TEST-HEADER'], 'aaa,bbb')

