pyswagger
=========

[![Build Status](https://travis-ci.org/AntXlab/pyswagger.svg?branch=master)](https://travis-ci.org/AntXlab/pyswagger)
[![Coverage Status](https://coveralls.io/repos/AntXlab/pyswagger/badge.png?branch=master)](https://coveralls.io/r/AntXlab/pyswagger?branch=master)

A python client for [Swagger](https://helloreverb.com/developers/swagger) enabled REST API. It wouldn't be easier to
try Swagger REST API by [Swagger-UI](https://github.com/wordnik/swagger-ui). However, when it's time to **unittest**
your API, the first option is [Swagger-codegen](https://github.com/wordnik/swagger-codegen), the second option is us.

**pyswagger** is much easier to use (you don't need to prepare a scala environment) and tries hard to fully supports
[Swagger Spec](https://helloreverb.com/developers/swagger)


- [Features](https://github.com/AntXlab/pyswagger/blob/master/README.md#features)
- [Quick Start](https://github.com/AntXlab/pyswagger/blob/master/README.md#quick-start)
- [Installation](https://github.com/AntXlab/pyswagger/blob/master/README.md#installation)
- [Reference](https://github.com/AntXlab/pyswagger/blob/master/README.md#reference)
- [Development](https://github.com/AntXlab/pyswagger/blob/master/README.md#development)
- [FAQ](https://github.com/AntXlab/pyswagger/blob/master/README.md#faq)

---------

##Features
- support Swagger **1.2** on python **2.6**, **2.7**, **3.3**, **3.4**
- type safe, input/output are converted according to [Data Type](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#43-data-types) described in swagger.
- builtin client implementation based on various http clients in python.
  - [requests](https://github.com/kennethreitz/requests)
  - [tornado.httpclient.AsyncHTTPClient](http://tornado.readthedocs.org/en/latest/httpclient.html)

---------

##Quick Start
```python
# load Swagger resource file into SwaggerApp object
app = SwaggerApp._create_('http://petstore.swagger.wordnik.com/api/api-docs')

# init SwaggerAuth for authorization
auth = SwaggerAuth(app)
auth.update_with('simple_basic_auth', ('user', '123123123'))
auth.update_with('simple_api_key', '123123123')

# init client
client = SwaggerClient(app, auth)

# a request to create a new pet
client.request(app.op['addPet'])(body=dict(id=1, name='Tom'))

# a request to get the pet back
pet = client.request(app.op['getPetById'])(petId=1).data
assert pet.id == 1
assert pet.name == 'Tom'
```


##Installation

---------

##Reference
###SwaggerApp
###SwaggerAuth
###SwaggerClient

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

