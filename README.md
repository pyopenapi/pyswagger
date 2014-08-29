pyswagger
=========

[![Build Status](https://travis-ci.org/AntXlab/pyswagger.svg?branch=master)](https://travis-ci.org/AntXlab/pyswagger)
[![Coverage Status](https://coveralls.io/repos/AntXlab/pyswagger/badge.png?branch=master)](https://coveralls.io/r/AntXlab/pyswagger?branch=master)

A python client for [Swagger](https://helloreverb.com/developers/swagger) enabled REST API. It wouldn't be easier to
try Swagger REST API by [Swagger-UI](https://github.com/wordnik/swagger-ui). However, when it's time to **unittest**
your API, the first option you find would be [Swagger-codegen](https://github.com/wordnik/swagger-codegen), but the best option is us.

**pyswagger** is much easier to use (you don't need to prepare a scala environment) and tries hard to fully supports
[Swagger Spec](https://helloreverb.com/developers/swagger) in all aspects.

**TODO:** File uploading (the last piece finally)


- [Features](https://github.com/AntXlab/pyswagger/blob/master/README.md#features)
- [Quick Start](https://github.com/AntXlab/pyswagger/blob/master/README.md#quick-start)
- [Installation](https://github.com/AntXlab/pyswagger/blob/master/README.md#installation)
- [Reference](https://github.com/AntXlab/pyswagger/blob/master/README.md#reference)
- [Development](https://github.com/AntXlab/pyswagger/blob/master/README.md#development)
- [FAQ](https://github.com/AntXlab/pyswagger/blob/master/README.md#faq)

---------

##Features
- support Swagger **1.2** on python **2.6**, **2.7**, **3.3**, **3.4**
- type safe, input/output are converted to python types according to [Data Type](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#43-data-types) described in swagger. You don't need to touch any json schema when using pyswagger. Limitations like **minimum/maximum** or **enum** are also checked. **Model inheritance** also supported.
- builtin client implementation based on various http clients in python.
  - [requests](https://github.com/kennethreitz/requests)
  - [tornado.httpclient.AsyncHTTPClient](http://tornado.readthedocs.org/en/latest/httpclient.html)

---------

##Quick Start
```python
from pyswagger import SwaggerApp, SwaggerAuth
from pyswagger.contrib.client.requests import Client

# load Swagger resource file into SwaggerApp object
app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')

# init SwaggerAuth for authorization
auth = SwaggerAuth(app)
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
```
##Installation
We support pip installtion.
```bash
pip install pyswagger
```
---------
##Reference
All exported API are described in following sections.

###SwaggerApp
The initialization of pyswagger starts from **SwaggerApp.\_create_(url)**, where **url** could either be a _url_ or a _file_ path. This function returns a SwaggerApp instance, which would be used to initiate SwaggerAuth.

**SwaggerApp.op** provides a shortcut to access Operation objects, which will produce a set of request/response for SwaggerClient to access API. The way we provide here would help to minimize the possible difference introduced by Swagger2.0 when everything is merged into one file.
```python
# call an API when its nickname is unique
SwaggerApp.op['getPetById']
# call an API when its nickname collid with other resources
SwaggerApp.op['user', 'getById'] # call getById in user resource
SwaggerApp.op['pet', 'getById']  # call getById in pet resource
```
###SwaggerClient
You also need **SwaggerClient(auth=None)** to access API, this layer wraps the difference between those http libraries in python. where **auth**(optional) is SwaggerAuth, which helps to handle authorizations of each request.

```python
client.request(app.op['addPet'](body=dict(id=1, name='Tom')))
```
To make a request, you need to create a pair of request/response from **SwaggerApp.op** by providing essential parameters. Then passing the tuple of (request, response) to **SwaggerClient.request(req_and_resp, opt={})** likes the code segment above. Below is a reference mapping between python objects and Swagger primitives. Check this mapping when you need to construct a parameter set:
- **dict** corresponds to _Model_
- **list** corresponds to _Array_
- **datetime.datetime**, timestamp, or ISO8601-string for _date-time_ and _date_
- other primitives are similar to python's primitives

The return value is a **SwaggerResponse** object, with these attributes:
- status
- data, corresponds to Operation object's return value, or ResponseMessage object's _responseModel_ when its status matched.
- header, organized in ```{key: [value1, value2...]}```
- message, corresponds to ResponseMessage object's _message_ when status matched on ResponseMessage object.
- raw, raw data without touching.

###SwaggerAuth
Holder/Dispatcher for user-provided authorization info. Initialize this object like **SwaggerAuth(app)**, where **app** is an instance of SwaggerApp. To add authorization, call **SwaggerAuth.update\_with(name, token)**, where **name** is the name of Authorizations object in Swagger spec, and **token** is different for different kinds of authorizations:
- basic authorization: (username, password)
- api key: the api key
- oauth2: the access\_token

---------

##Development
env preparation
```bash
pip install -r requirement-dev.txt
```

unit testing
```bash
python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc --cov-report=html pyswagger/tests
```

---------

##FAQ
- Format of date-time and date?
  - The preferred way is [json schema](http://xml2rfc.ietf.org/public/rfc/html/rfc3339.html#anchor14) according to this [issue](https://github.com/wordnik/swagger-spec/issues/95)
- Format of byte?
  - The way to encode/decode byte is [base64](https://github.com/wordnik/swagger-spec/issues/50).
- Format of datetime on the wire?
  - should be an ISO8601 string, according to this [issue](https://github.com/wordnik/swagger-spec/issues/95).
