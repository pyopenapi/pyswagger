from __future__ import absolute_import
import os
import sys

def get_test_data_folder(version='1.2', which=''):
    """
    """
    import pyswagger.tests.data

    version = 'v' + version.replace('.', '_')
    folder = os.path.dirname(os.path.abspath(pyswagger.tests.data.__file__))
    folder = os.path.join(os.path.join(folder, version), which)
    return folder


class DictDB(dict):
    """ Simple DB for singular model """
    def __init__(self):
        self._db = []

    def create_(self, **data):
        if len([elm for elm in self._db if elm['id'] == data['id']]):
            return False

        self._db.append(data)
        return True

    def read_(self, key):
        found = [elm for elm in self._db if elm['id'] == key]
        if len(found):
            return found[0]
        return None

    def update_(self, **data):
        for elm in self._db:
            if elm['id'] == data['id']:
                elm.update(data)
                return True
        return False

    def delete_(self, key):
        residual = [elm for elm in self._db if elm['id'] != key]
        found, self._db = (len(self._db) > len(residual)), residual
        return found

pet_Tom = dict(id=1, category=dict(id=1, name='dog'), name='Tom',  tags=[dict(id=2, name='yellow'), dict(id=3, name='big')], status='sold')
pet_Mary = dict(id=2, category=dict(id=2, name='cat'), name='Mary', tags=[dict(id=1, name='white'), dict(id=4, name='small')], status='pending')
pet_John = dict(id=3, category=dict(id=2, name='cat'), name='John', tags=[dict(id=2, name='yellow'), dict(id=4, name='small')], status='available')
pet_Sue = dict(id=4, category=dict(id=3, name='fish'), name='Sue', tags=[dict(id=5, name='gold'), dict(id=4, name='small')], status='available')

def create_pet_db():
    pet = DictDB()
    pet.create_(**pet_Tom)
    pet.create_(**pet_Mary)
    pet.create_(**pet_John)
    pet.create_(**pet_Sue)

    return pet

def is_windows():
    return os.name == 'nt'

def is_py2():
    return sys.version_info.major < 3

