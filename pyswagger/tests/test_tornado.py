from pyswagger.contrib.http.tornado import SwaggerClient
from tornado import web, testing
from .utils import create_pet_db, get_test_data_folder
import json


pet_db = create_pet_db()


""" refer to pyswagger.test.data.wordnik for details """


class BaseRequestHandler(web.RedirectHandler):
    """ base implementation of RequestHandler,
    accept a db as init paramaeter.
    """
    def initialize(self, db):
        self.db = db


class PetRequestHandler(BaseRequestHandler):
    """ refer to /pet """
    def put(self):
        pet = json.decode(self.get_body_argument('pet'))
        if not isinstance(pet['id'], int):
            self.set_status(400)

        if not self.db.update_(pet):
            self.set_status(404)

    def post(self):
        pet = json.decode(self.get_body_argument('pet'))
        self.db.create_(pet)


class PetIdRequestHandler(web.RequestHandler):
    """ refer to /pet/{petId} """
    def delete(self, id):
        if not self.db.delete_(id):
            self.set_status(400)

    def get(self, id):
        pet = self.db.read_(id)
        if not pet:
            self.set_status(404)
        else:
            self.write(json.encode(pet))


class TornadoTestCase(testing.AsyncHTTPTestCase):
    """
    """
    def setUp(self):
        self.client = SwaggerClient(get_test_data_folder('wordnik'))

    def get_app(self):
        global pet_db

        return web.Application([
            (r'/pet', PetRequestHandler, dict(db=pet_db)),
            (r'/pet/(\d+)', PetIdRequestHandler, dict(db=pet_db))
        ], debug=True)

    @testing.gen_test
    def test_pet_put(self):
        self.client.pet.updatePet()

    @testing.gen_test
    def test_pet_post(self):
        self.client.pet.addPet()

    @testing.gen_test
    def test_pet_id_delete(self):
        self.client.pet.deletePet()

    @testing.gen_test
    def test_pet_id_get(self):
        self.client.pet.getPetById()

