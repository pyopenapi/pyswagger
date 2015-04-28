.. pyswagger documentation master file, created by
   sphinx-quickstart on Tue Sep  2 20:23:09 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyswagger's documentation!
=====================================

**pyswagger** is a type-safe, dynamic, spec-complaint Swagger client.

- *type-safe*: Instead of manipulating json files as objects directly, we load them and produce our own object set. Every object in `Swagger spec <https://github.com/wordnik/swagger-spec>`_ has a correspondence in pyswagger. During construction of those objects, rules of Swagger Spec would be checked.
- *dynamic*: Unlike `swagger-codegen <https://github.com/wordnik/swagger-codegen>`_, pyswagger doesn't need preprocessing.
- *spec-complaint*: pyswagger support Swagger 1.2.

The main idea of pyswagger is to provide something easier to use than raw json, and develop things around that.


Contents
========

.. toctree::
    :maxdepth: 2

    topics/main
    topics/primitives
    topics/extend

Getting Started
===============

    .. code-block:: python

        from pyswagger import SwaggerApp, SwaggerSecurity
        from pyswagger.contrib.client.requests import Client

        # load Swagger resource file into SwaggerApp object
        app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')

        # init SwaggerSecurity for authorization
        auth = SwaggerSecurity(app)
        auth.update_with('simple_basic_auth', ('user', 'password')) # basic auth
        auth.update_with('simple_api_key', '12312312312312312313q') # api key
        auth.update_with('simple_oauth2', '12334546556521123fsfss') # oauth2

        # init swagger client
        client = Client(auth)

        # a request to create a new pet
        pet_Tom=dict(id=1, name='Tom') # a dict is enough
        client.request(app.op['addPet'](body=pet_Tom))

        # a request to get the pet back
        pet = client.request(app.op['getPetById'])(petId=1).data
        assert pet.id == 1
        assert pet.name == 'Tom'

        # redirect all requests targeting 'petstore.swagger.wordnik.com'
        # to 'localhost:9001' for testing locally
        client.request(
            app.op['addPet'](body=pet_Tom),
            opt={'url_netloc': 'localhost:9001'}
            )

        # allowMultiple parameter
        client.request(app.op['getPetsByStatus'](status='sold')) # one value
        client.request(app.op['getPetsByStatus'](status=['available', 'sold'])) # multiple value, wrapped by list.


`Source code <https://github.com/mission-liao/pyswagger>`_
`Report issues <https://github.com/mission-liao/pyswagger/issues>`_

