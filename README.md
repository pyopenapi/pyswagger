pyswagger
=========

[![Build Status](https://travis-ci.org/mission-liao/pyswagger.svg?branch=master)](https://travis-ci.org/mission-liao/pyswagger)
[![Coverage Status](https://coveralls.io/repos/mission-liao/pyswagger/badge.png?branch=master)](https://coveralls.io/r/mission-liao/pyswagger?branch=master)

A python client for [Swagger](https://helloreverb.com/developers/swagger) enabled REST API. It wouldn't be easier to
try Swagger REST API by [Swagger-UI](https://github.com/wordnik/swagger-ui). However, when it's time to **unittest**
your API, the first option you find would be [Swagger-codegen](https://github.com/wordnik/swagger-codegen), but the better option is us.

This project is developed after [swagger-py](https://github.com/digium/swagger-py), which is a nicely implemented one, and inspired many aspects of this project. Another project is [flex](https://github.com/pipermerriam/flex), which focuses on parameter validation, try it if you can handle other parts by yourselves.

For other projects related to Swagger tools in python, check [here](https://github.com/swagger-api/swagger-spec#python).

**pyswagger** is much easier to use (compared to swagger-codegen, you don't need to prepare a scala environment) and tries hard to fully supports [Swagger Spec](https://helloreverb.com/developers/swagger) in all aspects.

Read the [Document](http://pyswagger.readthedocs.org/en/latest/), or just go through this README.

- [Features](https://github.com/mission-liao/pyswagger/blob/master/README.md#features)
- [Quick Start](https://github.com/mission-liao/pyswagger/blob/master/README.md#quick-start)
- [Installation](https://github.com/mission-liao/pyswagger/blob/master/README.md#installation)
- [Reference](https://github.com/mission-liao/pyswagger/blob/master/README.md#reference)
- [Contributors](https://github.com/mission-liao/pyswagger/blob/master/README.md#contributors)
- [Contribution Guideline](https://github.com/mission-liao/pyswagger/blob/master/README.md#contribution-guideline)
- [FAQ](https://github.com/mission-liao/pyswagger/blob/master/README.md#faq)

---------

##Features
- support Swagger **1.2**, **2.0** on python **2.6**, **2.7**, **3.3**, **3.4**
- support $ref to **External Document**, multiple swagger.json will be organized into a group of SwaggerApp. And external document with self-describing resource is also supported (refer to [issue](https://github.com/swagger-api/swagger-spec/issues/219)).
- type safe, input/output are converted to python types according to [Data Type](https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md#43-data-types) described in Swagger. You don't need to touch any json schema when using pyswagger. Limitations like **minimum/maximum** or **enum** are also checked. **Model inheritance** also supported.
- provide function **SwaggerApp.validate** to check validity of the loaded API definition according to spec.
- builtin client implementation based on various http clients in python.
  - [requests](https://github.com/kennethreitz/requests)
  - [tornado.httpclient.AsyncHTTPClient](http://tornado.readthedocs.org/en/latest/httpclient.html)
- not implemented parts, fire me a bug if you need it
  - Swagger 2.0
    - Schema.pattern
    - Scheme.patternProperties
    - Schema.readonly
    - A scanner to validate schema
  - A WebSocket client
  - Pluggable primitive system, allowing to use new 'type' & 'format' in Swagger.

---------

##Quick Start
```python
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
  
# new ways to get Operation object corresponding to 'getPetById'
pet = client.request(app.resolve(jp_compose('/pet/{petId}', base='#/paths')).get(petId=1).data
assert pet.id == 1
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
The initialization of pyswagger starts from **SwaggerApp.\_create_(url)**, where **url** could either be a _url_ or a _file_ path. This function returns a SwaggerApp instance, which would be used to initiate SwaggerSecurity.

**SwaggerApp.op** provides a shortcut to access Operation objects, which will produce a set of request/response for SwaggerClient to access API. The way we provide here would help to minimize the possible difference introduced by Swagger2.0 when everything is merged into one file.
```python
# call an API when its nickname is unique
SwaggerApp.op['getPetById']
# call an API when its nickname collid with other resources
SwaggerApp.op['user', 'getById'] # operationId:'getById', tags:'user' (or a user resource in Swagger 1.2)
SwaggerApp.op['pet',  'getById'] # operationId:'getById', tags:'pet'  (or a pet resource in Swagger 1.2)

# utilize SwaggerApp.resolve to do the same thing
SwaggerApp.resolve('#/paths/~1pet~1{petId}').get
# instead of writing JSON-pointers by yourselves, utilize pyswagger.utils.jp_compose
SwaggerApp.resolve(utils.jp_compose('/pet/{petId}', base='#/paths')).get
```
**SwaggerApp.validate(strict=True)** provides validation against the loaded Swagger API definition. When passing _strict=True_, an exception would be raised if validation failed. It returns a list of errors in tuple: _(where, type, msg)_.

**SwaggerApp.resolve(JSON_Reference)** is a new way to access objects. For example, to access a Schema object 'User':
```python
app.resolve('#/definitions/User')
```
This function accepts a [JSON Reference](http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03), which is composed by an url and a [JSON Pointer](http://tools.ietf.org/html/rfc6901), it is the standard way to access a Swagger document. Since a JSON reference contains an url, this means you can access any external document when you need:
```python
app.resolve('http://another_site.com/apis/swagger.json#/definitions/User')
```
pyswagger will load that swagger.json, create a new SwaggerApp, and group it with the SwaggerApp you kept (**app** in code above). Internally, when pyswagger encounter some $ref directs to external documents, we just silently handle it in the same way.

###SwaggerClient
You also need **SwaggerClient(security=None)** to access API, this layer wraps the difference between those http libraries in python. where **security**(optional) is SwaggerSecuritysw, which helps to handle authorizations of each request.

```python
client.request(app.op['addPet'](body=dict(id=1, name='Tom')))
```
To make a request, you need to create a pair of request/response from **SwaggerApp.op** by providing essential parameters. Then passing the tuple of (request, response) to **SwaggerClient.request(req_and_resp, opt={})** likes the code segment above. Below is a reference mapping between python objects and Swagger primitives. Check this mapping when you need to construct a parameter set:
- **dict** corresponds to _Model_
- **list** corresponds to _Array_
- **datetime.datetime**, timestamp(float or int), or ISO8601-string for _date-time_ and _date_
- _File_ type is a little bit complex, but just similar to [request](https://github.com/kennethreitz/requests), which uses a dict containing file info.
```python
YouFile = {
  # header values used in multipart/form-data according to RFC2388
  'header': {
    'Content-Type': 'text/plain',
    
    # according to RFC2388, available values are '7bit', '8bit', 'binary'
    'Content-Transfer-Encoding': 'binary'
  },
  'filename': 'a.txt',
  'data': None (or any file-like object)
}
```
- other primitives are similar to python's primitives

The return value is a **SwaggerResponse** object, with these attributes:
- status
- data, corresponds to Operation object's return value, or ResponseMessage object's _responseModel_ when its status matched.
- header, organized in ```{key: [value1, value2...]}```
- message, corresponds to ResponseMessage object's _message_ when status matched on ResponseMessage object.
- raw, raw data without touching.

###SwaggerSecurity
Holder/Dispatcher for user-provided authorization info. Initialize this object like **SwaggerSecurity(app)**, where **app** is an instance of SwaggerApp. To add authorization, call **SwaggerSecurity.update\_with(name, token)**, where **name** is the name of Authorizations object in Swagger 1.2(Security Scheme Object in Swagger 2.0) , and **token** is different for different kinds of authorizations:
- basic authorization: (username, password)
- api key: the api key
- oauth2: the access\_token

---------

##Contributors
- [Marcin Goliński](https://github.com/mjgolinski)
- [Andrey Mikhailov](https://github.com/zlovred)

---------

##Contribution Guildeline
report an issue:
- issues can be reported [here](https://github.com/mission-liao/pyswagger/issues)
- include swagger.json if possible
- describe expected behavior, or more specific, the input/output

request a merge
- try not to decrease the coverage rate
- test included

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
- Format of byte?
  - The way to encode/decode byte is [base64](https://github.com/wordnik/swagger-spec/issues/50).
- Format of datetime on the wire?
  - should be an ISO8601 string, according to this [issue](https://github.com/wordnik/swagger-spec/issues/95).
- How **allowMultiple** is handled?
  - Take type integer as example, you can pass ~~an integer or~~ an array/tuple of integer for this parameter. (a single value is no longer supported)
- What do we need to take care of when upgrading from Swagger 1.2 to 2.0?
  - **allowMultiple** is no longer supported, always passing an array even with a single value.
  - 'different host for different resource' is no longer supported in Swagger 2.0, only one host and one basePath is allowed in one swagger.json.
  - refer to [Migration Guide](https://github.com/swagger-api/swagger-spec/wiki/Swagger-1.2-to-2.0-Migration-Guide) from Swagger team.
