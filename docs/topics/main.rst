===============
Main Components
===============

*SwaggerApp*, *SwaggerSecurity*, *Client* are components you would touch first when adapting pyswagger.

SwaggerApp
==========

SwaggerApp carries Swagger API definition, other components would rely on it but not json files. You need to access Operation object via **SwaggerApp.op** by providing *nickname* or *resource name* plus *nickname*.

.. code-block:: python

    app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')
    assert app.op['getPetsByStatus'] == app.op['pet', 'getPetsByStatus']

    # resource name is must when nickname collid
    app.op['user', 'getById']
    app.op['pet', 'getById']

The Operation object is callable, and can be provided by a set of :ref:`primitives`, then return a pair of :ref:`SwaggerRequest` and :ref:`SwaggerResponse`.

SwaggerSecurity
===========

SwaggerSecurity is a placeholder of authorizations,

.. code-block:: python

    # must be initialized with SwaggerApp
    auth = SwaggerSecurity(app)

    # insert autorization information
    app.update_with('simple_basicAuth', ('user', 'password'))
    app.update_with('simple_apiKey', 'token123')
    app.update_with('simple_oath2', 'token123456')

    # pass into a client
    client = TornadoClient(auth)

    # authorization would be applied automatically
    client.request(...)


Client
======

Clients are wrapper layer to hide implementation details from different http-request libraries.

To implement a customized client, please refer to :ref:`customized client <extend_client>`

Below is a code to demostrate the relation between these components.

.. code-block:: python

    app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')
    auth = SwaggerSecurity(app)
    client = Client(auth)

    # get SwaggerRequest and SwaggerResponse from Swagger.op
    req, resp = app.op['getPetById'](Id=1)

    # call request
    resp = client.request((req, resp))

    # get data back
    assert resp.data.id == 1
    

Reference
=========

.. module:: pyswagger.core
.. autoclass:: SwaggerApp
    :members:
    :private-members:

.. autoclass:: SwaggerSecurity
    :members:

    .. automethod:: __init__
    .. automethod:: __call__

.. module:: pyswagger.contrib.client.requests
.. autoclass:: Client

.. module:: pyswagger.contrib.client.tornado
.. autoclass:: TornadoClient

.. module:: pyswagger.io


.. _SwaggerRequest:

##############
SwaggerRequest
##############

.. autoclass:: SwaggerRequest
    :members:

.. _SwaggerResponse:

###############
SwaggerResponse
###############

.. autoclass:: SwaggerResponse
    :members:
