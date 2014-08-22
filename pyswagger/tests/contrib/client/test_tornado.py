from tornado import web, testing
from ...utils import create_pet_db, get_test_data_folder
import json


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


""" global variables """

pet_db = create_pet_db()
app = web.Application([
            (r'/pet', PetRequestHandler, dict(db=pet_db)),
            (r'/pet/(\d+)', PetIdRequestHandler, dict(db=pet_db))
        ], debug=True)


class TornadoTestCase(testing.AsyncHTTPTestCase):
    """
    """
    def setUp(self):
        super(TornadoTestCase, self).setUp()

    def get_app(self):
        global app
        return app

    @testing.gen_test
    def test_pet_put(self):
        pass

    @testing.gen_test
    def test_pet_post(self):
        pass

    @testing.gen_test
    def test_pet_id_delete(self):
        pass

    @testing.gen_test
    def test_pet_id_get(self):
        pass

