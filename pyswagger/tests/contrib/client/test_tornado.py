from __future__ import absolute_import
from tornado import web, testing
from tornado.ioloop import IOLoop
from pyswagger import SwaggerApp
from pyswagger.contrib.client.tornado import TornadoClient
from ...utils import create_pet_db, get_test_data_folder, pet_Mary
import json
import sys
import pytest


sapp = SwaggerApp._create_(get_test_data_folder(version='1.2', which='wordnik')) 

""" refer to pyswagger.tests.data.v1_2.wordnik for details """

class RESTHandler(web.RequestHandler):
    """ base implementation of RequestHandler,
    accept a db as init paramaeter.
    """
    def initialize(self, db):
        self.db = db

    def prepare(self):
        """
        According to FAQ of tornado, they won't handle json media-type.
        """
        super(RESTHandler, self).prepare()

        content_type = self.request.headers.get('Content-Type')
        if content_type and content_type.startswith('application/json'):
            # handle media-type: json
            if content_type.rfind('charset=UTF-8'):
                self.json_args = json.loads(self.request.body.decode('utf-8'))
            else:
                raise web.HTTPError('unsupported application type:' + content_type)


class PetRequestHandler(RESTHandler):
    """ refer to /pet """
    def put(self):
        pet = self.json_args['body']
        if not isinstance(pet['id'], int):
            self.set_status(400)
        if not self.db.update_(**pet):
            self.set_status(404)
        else:
            self.set_status(200)
        self.finish()

    def post(self):
        pet = self.json_args['body']
        if self.db.read_(pet['id']) != None:
            self.set_status(409)
        else:
            self.db.create_(**pet)
            self.set_status(200)
        self.finish()


class PetIdRequestHandler(RESTHandler):
    """ refer to /pet/{petId} """
    def delete(self, id):
        if not self.db.delete_(int(id)):
            self.set_status(400)
        self.finish()

    def get(self, id):
        pet = self.db.read_(int(id))
        if not pet:
            self.set_status(404)
        else:
            self.write(json.dumps(pet))
        self.finish()


""" global variables """

pet_db = create_pet_db()
app = web.Application([
    (r'/api/pet', PetRequestHandler, dict(db=pet_db)),
    (r'/api/pet/(\d+)', PetIdRequestHandler, dict(db=pet_db))
], debug=True)


@pytest.mark.skipif(sys.version_info[:2] >= (3, 4), reason='httpretty corrupt tornado.testing in python3.4')
class TornadoTestCase(testing.AsyncHTTPTestCase):
    """
    """
    def setUp(self):
        super(TornadoTestCase, self).setUp()
        self.client = TornadoClient(app)

    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        global app
        return app

    @testing.gen_test
    def test_updatePet(self):
        """ updatePet """
        global pet_db
        resp = yield self.client.request(
            sapp.op['updatePet'](body=dict(id=1, name='Tom1')),
            opt=dict(
                url_netloc='localhost:'+str(self.get_http_port())
            ))

        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(1)['name'], 'Tom1')

    @testing.gen_test
    def test_addPet(self):
        """ addPet """
        global pet_db

        resp = yield self.client.request(
            sapp.op['addPet'](body=dict(id=5, name='Mission')),
            opt=dict(
                url_netloc='localhost:'+str(self.get_http_port())
            ))

        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(5)['name'], 'Mission')

    @testing.gen_test
    def test_deletePet(self):
        """ deletePet """
        resp = yield self.client.request(
            sapp.op['deletePet'](petId=5),
            opt=dict(
                url_netloc='localhost:'+str(self.get_http_port())
            ))

        self.assertEqual(resp.status, 200)
        self.assertEqual(pet_db.read_(5), None)

    @testing.gen_test
    def test_getPetById(self):
        """ getPetById """
        resp = yield self.client.request(
            sapp.op['getPetById'](petId=2),
            opt=dict(
                url_netloc='localhost:'+str(self.get_http_port())
            ))

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.data, pet_Mary)

