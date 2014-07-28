from __future__ import absolute_import
import os

def get_test_data_folder(which=""):
    """
    """
    import pyswagger.tests.data

    folder = os.path.dirname(pyswagger.tests.data.__file__)
    if which != None:
        folder = os.path.join(folder, which)
    return folder

